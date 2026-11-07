"""Actual Brain functional compensation and serialized fingerprint tests."""
from dataclasses import replace
import json
import unittest
from neurogenesis.brain import Brain, BrainConfig
from neurogenesis.repair import lesioned_copy
from neurogenesis.lesion_benchmark import _sequence, fingerprint_repair_benchmark
from neurogenesis.fingerprint_repair import (
    ActivityFingerprint, record_fingerprint, fingerprint_error,
    propose_fingerprint_repair,
)


def reference(seed=1, steps=50):
    brain = Brain(replace(BrainConfig(), growth_enabled=False), seed=seed)
    for x in _sequence(seed=seed, steps=steps, noisy=False):brain.step(x)
    return brain


class FingerprintTests(unittest.TestCase):
    def test_recording_is_read_only_and_roundtrips_canonically(self):
        healthy = reference()
        old = healthy.to_dict()
        data = list(_sequence(seed=22, steps=42, noisy=False))
        record = record_fingerprint(healthy, data)
        self.assertEqual(record.to_dict(), ActivityFingerprint.from_dict(
            json.loads(json.dumps(record.to_dict()))).to_dict())
        self.assertEqual(healthy.to_dict(), old)
        self.assertEqual(fingerprint_error(healthy, record), 0.0)

    def test_repair_improves_validation_and_holdout_for_one_sample(self):
        healthy = reference(1, steps=160)
        record = record_fingerprint(healthy, list(_sequence(seed=10001, steps=72, noisy=False)))
        broken = lesioned_copy(healthy, fraction=0.5, seed=991)
        snapshot = broken.to_dict()
        output, report = propose_fingerprint_repair(broken, record)
        self.assertGreater(report.initial_error, report.final_validation_error)
        self.assertGreater(report.accepted_connections, 0)
        self.assertEqual(broken.to_dict(), snapshot)
        self.assertEqual(output.to_dict()['schema'], snapshot['schema'])
        self.assertLessEqual(len(output.synapses), output.config.max_synapses)

    def test_no_repair_is_attempted_when_no_damage_evidence(self):
        healthy = reference()
        record = record_fingerprint(healthy, list(_sequence(seed=99, steps=40, noisy=False)))
        output, result = propose_fingerprint_repair(healthy, record)
        self.assertEqual(result.initial_error, 0)
        self.assertEqual(result.accepted_connections, 0)
        self.assertEqual(output.to_dict(), healthy.to_dict())

    def test_budget_zero_is_noop_and_validates_signature(self):
        healthy = reference()
        record = record_fingerprint(healthy, list(_sequence(seed=99, steps=40, noisy=False)))
        broken = lesioned_copy(healthy, fraction=.5, seed=7)
        out, result = propose_fingerprint_repair(broken, record, max_new_synapses=0)
        self.assertEqual(result.accepted_connections, 0)
        self.assertEqual(out.to_dict(), broken.to_dict())
        with self.assertRaises(ValueError):
            propose_fingerprint_repair(broken, record, max_new_synapses=9)

    def test_corrupt_fingerprint_fails_closed(self):
        healthy = reference()
        data = record_fingerprint(healthy, list(_sequence(seed=9, steps=12, noisy=False))).to_dict()
        bads = [dict(data, schema=12), dict(data, input_size=9),
                dict(data, responses=[[]]), dict(data, stimuli=[['bad']]),
                dict(data, stimuli=[[float('nan')]*8]), dict(data, hi=5)]
        for item in bads:
            with self.subTest(item=str(item)[:40]), self.assertRaises((ValueError, TypeError)):
                ActivityFingerprint.from_dict(item)

    def test_fingerprint_mismatch_fails_closed(self):
        healthy = reference()
        record = record_fingerprint(healthy, list(_sequence(seed=9, steps=12, noisy=False)))
        bigger = Brain(BrainConfig(initial_neurons=25, max_neurons=128),seed=5)
        with self.assertRaises(ValueError):fingerprint_error(bigger,record)
        with self.assertRaises(ValueError):propose_fingerprint_repair(bigger,record)

    def test_strict_eval_budget_and_invalid_configs(self):
        healthy=reference(2)
        record=record_fingerprint(healthy,list(_sequence(seed=11,steps=40,noisy=False)))
        damaged=lesioned_copy(healthy,fraction=.5,seed=2)
        for kwargs in ({'max_proposals':-1},{'max_proposals':True},
                       {'min_improvement':float('nan')},{'max_new_synapses':True}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                propose_fingerprint_repair(damaged,record,**kwargs)
        clone, report = propose_fingerprint_repair(damaged,record,max_proposals=1)
        self.assertLessEqual(report.attempted_proposals,1)
        self.assertEqual(len(clone.voltages),len(damaged.voltages))

    def test_benchmark_reproducible_on_true_brain_and_no_holdout_leak(self):
        a=fingerprint_repair_benchmark(seeds=3)
        b=fingerprint_repair_benchmark(seeds=3)
        self.assertEqual(a,b)
        self.assertEqual(len(a['paired_results']),3)
        self.assertEqual(a['improved_holdout_seeds'],3)
        self.assertIn('not generalization',a['limitations'])

    def test_max_size_and_empty_signature_rejected(self):
        b=reference()
        with self.assertRaises(ValueError):record_fingerprint(b,[])
        with self.assertRaises(ValueError):record_fingerprint(b,[[1.0]*8]*257)
        with self.assertRaises(ValueError):record_fingerprint(b,[[float('inf')]*8])
        with self.assertRaises(ValueError):record_fingerprint(b,[['a']*8])
        with self.assertRaises(ValueError):record_fingerprint(b,[[True]*8])
        with self.assertRaises(ValueError):record_fingerprint(b,[[1.0]*7])

if __name__ == '__main__':unittest.main()

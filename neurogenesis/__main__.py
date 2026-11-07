"""Offline-first research CLI. No autonomous internet or self-modifying code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from .brain import Brain
from .experiment import compare_growth
from .self_model import inspect
from .predictor import prediction_control
from .sensory import TextSensor
from .origin import origin_record
from .benchmark import continual_learning_benchmark


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="neurogenesis", description="Experimental neuroplasticity research baseline")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="run a deterministic neural growth demonstration")
    demo.add_argument("--steps", type=int, default=160)
    demo.add_argument("--state", type=Path, help="optional output JSON snapshot")
    compare = commands.add_parser("compare", help="compare growth ON vs OFF with identical inputs")
    compare.add_argument("--steps", type=int, default=160)
    predict = commands.add_parser("predict", help="measure online next-input prediction vs fixed structure")
    predict.add_argument("--steps", type=int, default=400)
    benchmark = commands.add_parser("benchmark", help="A-B-A learning/retention on paired seeds")
    benchmark.add_argument("--seeds", type=int, default=10)
    benchmark.add_argument("--steps-per-phase", type=int, default=160)
    benchmark.add_argument("--probe-steps", type=int, default=64)
    benchmark.add_argument("--noise", type=float, default=0.15)
    observe = commands.add_parser("observe", help="encode user text as sensory input (NOT conversation)")
    observe.add_argument("text", help="text to encode")
    observe.add_argument("--state", type=Path, required=True, help="state JSON to create/update")
    status = commands.add_parser("status", help="inspect saved state without executing it")
    status.add_argument("--state", type=Path, required=True)
    commands.add_parser("origin", help="show recorded initiator, contributors and mission")
    args = parser.parse_args(argv)
    try:
        if args.command == "origin":
            result = origin_record()
        elif args.command == "benchmark":
            result = continual_learning_benchmark(seeds=args.seeds,
                          steps_per_phase=args.steps_per_phase,
                          probe_steps=args.probe_steps, noise=args.noise)
        elif args.command == "predict":
            result = prediction_control(steps=args.steps)
        elif args.command == "compare":
            result = compare_growth(steps=args.steps)
        elif args.command == "status":
            result = inspect(Brain.load(args.state))
        elif args.command == "observe":
            brain = Brain.load(args.state) if args.state.exists() else Brain()
            features = TextSensor(brain.config.input_size).encode(args.text)
            for _ in range(4):
                brain.step(features)
            brain.save(args.state)
            result = {"input": "hashed_text_features", "features": features, "self_model": inspect(brain)}
        else:
            if not 1 <= args.steps <= 100_000:
                raise ValueError("steps must be in [1, 100000]")
            brain = Brain()
            for step in range(args.steps):
                stimulus = [0.0] * brain.config.input_size
                stimulus[(step // 4) % brain.config.input_size] = 1.0
                stimulus[((step // 4) + 2) % brain.config.input_size] = 1.0
                brain.step(stimulus)
            if args.state:
                brain.save(args.state)
            result = inspect(brain)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"neurogenesis: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())

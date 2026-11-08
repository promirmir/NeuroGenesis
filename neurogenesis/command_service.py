"""Qt-independent adapter exposing real local brain, evidence and study state.

No PyTorch, Qt or Internet import happens by launching the legacy Windows app.
Research is opt-in and network-disabled on each new process startup.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path
import queue
import threading
from typing import Any, Callable

from .desktop import default_db_path, process_message
from .memory import ExperienceMemory
from .specialist_study import SpecialistStudy


@dataclass(frozen=True)
class CommandSnapshot:
    cpu_threads: int | None
    database: str
    observations: int
    documents: int
    passages: int
    neurons: int
    synapses: int
    brain_steps: int
    network_enabled: bool
    research_running: bool
    research_attempted: int
    research_accepted: int
    research_errors: int
    research_discovered: int
    research_domains: int
    training_running: bool
    training_step: int
    training_total: int
    training_last_loss: float | None
    inference_running: bool
    memory_maintenance_running: bool


class CommandService:
    """Actual service boundary: Qt widgets never own SQLite or fetch a URL."""

    def __init__(self, db_path: str | Path | None = None, *,
                 study_factory: Callable[..., Any] = SpecialistStudy):
        self.memory = ExperienceMemory(db_path if db_path is not None else default_db_path())
        self.memory.status()  # detect broken neural checkpoint, never silently reset
        self._consent = False
        self._state_lock = threading.Lock()
        self._study: Any = None
        self._thread: threading.Thread | None = None
        self._events: queue.SimpleQueue[tuple[str, str]] = queue.SimpleQueue()
        self._study_factory = study_factory
        self._training_thread: threading.Thread | None = None
        self._training_cancel: threading.Event | None = None
        self._training_step = 0
        self._training_total = 0
        self._training_last_loss: float | None = None
        self._inference_thread: threading.Thread | None = None
        self._inference_cancel: threading.Event | None = None
        self._memory_maintenance: threading.Thread | None = None
        # Volatile ONLY: no raw conversation history is saved to SQLite.
        self._last_grounded_question: str | None = None
        self._last_grounded_source_url: str | None = None

    @property
    def network_enabled(self) -> bool:
        with self._state_lock:
            return self._consent

    def set_network_consent(self, consent: bool) -> None:
        if type(consent) is not bool:
            raise ValueError("network consent must be an explicit boolean")
        with self._state_lock:
            self._consent = consent
            study = self._study
        if not consent and study is not None:
            study.stop()
            self._events.put(("state", "Zgoda cofnięta — zatrzymywanie badania"))

    def snapshot(self) -> CommandSnapshot:
        current = self.memory.status()
        bs = current["brain"]
        with self._state_lock:
            study = self._study
            thread = self._thread
            network = self._consent
            training_thread = self._training_thread
            training_step = self._training_step
            training_total = self._training_total
            training_last_loss = self._training_last_loss
            inference_thread = self._inference_thread
            maintenance_thread = self._memory_maintenance
        progress = study.progress() if study is not None else None
        return CommandSnapshot(
            cpu_threads=os.cpu_count(), database=str(self.memory.path),
            observations=current["observations"],
            documents=current["knowledge"]["documents"],
            passages=current["knowledge"]["passages"],
            neurons=bs["neurons"], synapses=bs["synapses"],
            brain_steps=bs["steps"], network_enabled=network,
            research_running=thread is not None and thread.is_alive(),
            research_attempted=progress.attempted if progress else 0,
            research_accepted=progress.accepted if progress else 0,
            research_errors=progress.errors if progress else 0,
            research_discovered=progress.discovered if progress else 0,
            research_domains=progress.domains if progress else 0,
            training_running=training_thread is not None and training_thread.is_alive(),
            training_step=training_step, training_total=training_total,
            training_last_loss=training_last_loss,
            inference_running=inference_thread is not None and inference_thread.is_alive(),
            memory_maintenance_running=(maintenance_thread is not None
                                        and maintenance_thread.is_alive()))

    def ask(self, question: str) -> dict[str, Any]:
        from .dialogue_context import expand_followup
        with self._state_lock:
            previous_question = self._last_grounded_question
            previous_url = self._last_grounded_source_url
        proposal = (expand_followup(question, previous_question)
                    if previous_question is not None and previous_url is not None else None)
        if proposal is None:
            result = process_message(self.memory, question)
        else:
            # Both the old anchor URL and novel lexical terms must appear
            # in the same saved, newest-revision passage to answer.
            result = process_message(
                self.memory, question, evidence_query=proposal.query,
                evidence_source_url=previous_url,
                evidence_focus_terms=proposal.mandatory_focus_terms)
        with self._state_lock:
            if result["response_kind"] == "source_evidence":
                if proposal is None:
                    self._last_grounded_question = question
                    self._last_grounded_source_url = result["sources"][0]["url"]
            else:
                # No stale topic may leak through an intervening failed
                # question, new teaching or unrelated conversational turn.
                self._last_grounded_question = None
                self._last_grounded_source_url = None
        return result

    def start_memory_backup(self, destination: str | Path) -> None:
        """Save verified consistent SQLite snapshot on a background thread."""
        self._memory_job("backup", Path(destination))

    def start_memory_verification(self, snapshot: str | Path) -> None:
        """Check selected backup without changing it or the live memory."""
        self._memory_job("verify", Path(snapshot))

    def _memory_job(self, action: str, path: Path) -> None:
        if action not in ("backup", "verify"):
            raise ValueError("unsupported memory action")
        with self._state_lock:
            if self._memory_maintenance is not None and self._memory_maintenance.is_alive():
                raise RuntimeError("Trwa już kopia lub kontrola integralności")
            if self._training_thread is not None and self._training_thread.is_alive():
                raise RuntimeError("Zakończ trening przed tworzeniem kopii pamięci")
            def run() -> None:
                try:
                    from .recovery import backup_private_database, inspect_private_database
                    data = (backup_private_database(self.memory.path, path)
                            if action == "backup"
                            else inspect_private_database(path))
                    self._events.put(("memory_" + action + "_done",
                                      json.dumps(data, ensure_ascii=False)))
                except Exception as exc:
                    # No paths or sensitive SQLite contents in public logs;
                    # UI only receives a bounded local error category.
                    self._events.put(("memory_" + action + "_failed",
                                      type(exc).__name__))
            self._memory_maintenance = threading.Thread(
                target=run, name="NeuroGenesis-private-memory-maintenance", daemon=True)
            self._memory_maintenance.start()

    def clear_conversation_context(self) -> None:
        """Forget only transient topic carryover, never persistent SQLite."""
        with self._state_lock:
            self._last_grounded_question = None
            self._last_grounded_source_url = None

    def teach(self, question: str, answer: str) -> dict[str, Any]:
        return self.memory.teach(question, answer)

    def sources(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.memory.knowledge_sources(limit=limit)

    def source_passages(self, source_id: int) -> list[dict[str, Any]]:
        return self.memory.knowledge_passages(source_id)

    def neural_frame(self):
        """Read an actual persisted bounded LIF synapse/spike snapshot."""
        from .neural_graph import snapshot_brain
        return snapshot_brain(self.memory.brain())

    def neural_traces(self) -> tuple[float, ...]:
        return tuple(self.memory.brain().traces)

    def set_source_training_rights(self, source_id: int, approved: bool) -> dict[str, Any]:
        if approved is False:
            # An in-progress worker must not keep writing a candidate after
            # permission is revoked through this desktop service.
            self.stop_training()
        return self.memory.set_source_training_rights(source_id, approved)

    def start_training(self, output: str | Path, *, confirmed: bool,
                       steps: int, device: str, sequence: int = 32,
                       hidden: int = 32, resume_from: str | Path | None = None,
                       trust_resume: bool = False) -> None:
        """Operator-only, bounded Torch worker, never auto-started by GUI."""
        if confirmed is not True:
            raise PermissionError("Potwierdź prawa do zatwierdzonych dokumentów")
        # Checking installation must not import the heavyweight framework on
        # Qt's UI thread; actual PyTorch initialization happens in the worker.
        if importlib.util.find_spec("torch") is None:
            raise RuntimeError("Zainstaluj opcjonalny PyTorch: pip install -e '.[foundation]'")
        if len(self.memory.approved_training_documents()) < 3:
            raise ValueError("Zatwierdź prawa do co najmniej 3 aktualnych dokumentów")
        if resume_from is not None:
            if trust_resume is not True:
                raise PermissionError("Potwierdź zaufany lokalny checkpoint")
            path = Path(resume_from)
            if not path.is_file() or path.is_symlink() or path.suffix.lower() not in (".pt", ".pth"):
                raise ValueError("Wybierz poprawny, istniejący checkpoint do kontynuacji")
            if path.resolve() == Path(output).resolve():
                raise ValueError("Wynik musi być zapisany do nowego pliku, nie do poprzedniego")
        with self._state_lock:
            if self._training_thread is not None and self._training_thread.is_alive():
                raise RuntimeError("Trening jest już aktywny")
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("Zatrzymaj badanie źródeł przed treningiem")
            if self._inference_thread is not None and self._inference_thread.is_alive():
                raise RuntimeError("Zatrzymaj eksperyment generowania przed treningiem")
            self._training_cancel = threading.Event()
            cancel = self._training_cancel
            self._training_step = 0
            self._training_total = steps
            self._training_last_loss = None

            def progress(step: int, metrics: dict[str, float]) -> None:
                with self._state_lock:
                    self._training_step = step
                    self._training_last_loss = metrics["loss"]
                self._events.put(("train_progress", json.dumps({
                    "step": step, "total": steps, "loss": metrics["loss"]})))

            def run() -> None:
                try:
                    from .knowledge_train import train_approved_knowledge
                    report = train_approved_knowledge(
                        self.memory.path, output, confirm_rights=True,
                        steps=steps, sequence=sequence, hidden=hidden,
                        device=device, resume_from=resume_from,
                        trust_resume=trust_resume,
                        cancel_event=cancel, on_progress=progress)
                    self._events.put(("train_done", json.dumps(report)))
                except InterruptedError:
                    self._events.put(("train_cancelled",
                                      "Zatrzymano bez instalacji checkpointu"))
                except Exception as exc:
                    self._events.put(("train_fatal", type(exc).__name__ + ": " + str(exc)))

            self._training_thread = threading.Thread(
                target=run, name="NeuroGenesis-Foundation-training", daemon=True)
            self._training_thread.start()

    def stop_training(self) -> None:
        with self._state_lock:
            cancel = self._training_cancel
        if cancel is not None:
            cancel.set()

    def start_candidate_inference(self, checkpoint: str | Path, prompt: str, *,
                                  confirmed: bool, max_new_bytes: int = 32,
                                  device: str = "cpu") -> None:
        """Run real checkpoint logits without promoting raw output to chat."""
        if confirmed is not True:
            raise PermissionError("Potwierdź zaufane pochodzenie lokalnego checkpointu")
        if importlib.util.find_spec("torch") is None:
            raise RuntimeError("PyTorch nie jest zainstalowany")
        # Reject invalid requests before launching the worker.
        if type(prompt) is not str or len(prompt) > 512 or len(prompt.encode("utf-8")) < 2:
            raise ValueError("Wprowadź 2+ bajty UTF-8 i maksymalnie 512 znaków")
        if type(max_new_bytes) is not int or not 1 <= max_new_bytes <= 64:
            raise ValueError("Limit wynosi 1–64 bajty")
        if device not in ("cpu", "cuda"):
            raise ValueError("Nieprawidłowe urządzenie")
        path = Path(checkpoint)
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in (".pt", ".pth"):
            raise ValueError("Wskaż istniejący, lokalny checkpoint .pt/.pth")
        with self._state_lock:
            if self._inference_thread is not None and self._inference_thread.is_alive():
                raise RuntimeError("Eksperyment wnioskowania już trwa")
            if self._training_thread is not None and self._training_thread.is_alive():
                raise RuntimeError("Zatrzymaj trening przed wnioskowaniem")
            self._inference_cancel = threading.Event()
            cancel = self._inference_cancel

            def run() -> None:
                try:
                    from .foundation_infer import generate_candidate
                    report = generate_candidate(
                        path, prompt, trust_checkpoint=True, device=device,
                        max_new_bytes=max_new_bytes, cancel_event=cancel)
                    self._events.put(("inference_done", json.dumps(report, ensure_ascii=False)))
                except InterruptedError:
                    self._events.put(("inference_cancelled", "Zatrzymano eksperyment"))
                except Exception as exc:
                    self._events.put(("inference_fatal", type(exc).__name__ + ": " + str(exc)))

            self._inference_thread = threading.Thread(
                target=run, name="NeuroGenesis-Foundation-inference", daemon=True)
            self._inference_thread.start()

    def stop_candidate_inference(self) -> None:
        with self._state_lock:
            cancel = self._inference_cancel
        if cancel is not None:
            cancel.set()

    def start_study(self, topic: str, pages: int) -> None:
        with self._state_lock:
            if not self._consent:
                raise PermissionError("Włącz jawną zgodę HTTPS przed badaniem")
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("Inna sesja badawcza już trwa")
            if self._training_thread is not None and self._training_thread.is_alive():
                raise RuntimeError("Zatrzymaj trening przed pobieraniem źródeł")
            # Constructing the study is offline: plan_topic does not fetch.
            def persist(observation):
                # Revocation before the write must also stop in-flight reads
                # from adding new data. SQLite transaction is synchronous.
                with self._state_lock:
                    if not self._consent:
                        raise PermissionError("Zgoda HTTPS została cofnięta")
                return self.memory.observe_web(observation)

            study = self._study_factory(topic, persist, max_pages=pages)
            self._study = study

            def run() -> None:
                try:
                    study.run(consent=True, on_event=lambda event, url:
                              self._events.put((event, url)))
                except Exception as exc:
                    # Only exception class is exposed; no private URLs or stack
                    # traces are transmitted to a service outside the process.
                    self._events.put(("fatal", type(exc).__name__))
                finally:
                    self._events.put(("done", ""))

            self._thread = threading.Thread(
                target=run, name="NeuroGenesis-Qt-research", daemon=True)
            self._thread.start()
        self._events.put(("state", "Rozpoczęto kontrolowane badanie: " + study.topic))

    def stop_study(self) -> None:
        with self._state_lock:
            study = self._study
        if study is not None:
            study.stop()
            self._events.put(("state", "Zatrzymywanie po bieżącym żądaniu"))

    def poll_events(self, limit: int = 100) -> list[tuple[str, str]]:
        if type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError("invalid event limit")
        out = []
        for _ in range(limit):
            try:
                out.append(self._events.get_nowait())
            except queue.Empty:
                break
        return out

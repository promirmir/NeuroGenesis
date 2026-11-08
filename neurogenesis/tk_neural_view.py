"""Futuristic but factual Tk canvas visualization of the persisted LIF graph.

All foreground neurons, synapses, traces, spikes and counters are sourced from
BrainFrame. Cosmetic grid/glow is not itself telemetry. No animation at idle.
"""
from __future__ import annotations

from .neural_graph import BrainFrame, positions


BACKGROUND = "#081222"
GRID = "#12273d"
QUIET = "#1c3854"
LINK = "#2a6482"
INPUT = "#37bafa"
NEURON = "#59dacf"
SPIKE = "#ffb84c"


def render_tk_graph(canvas, frame: BrainFrame, *, event_age: float = 10.0) -> None:
    """Draw a responsive graph. Event flashes represent ONLY newly observed steps."""
    width = max(420, canvas.winfo_width())
    height = max(300, canvas.winfo_height())
    canvas.delete("all")
    canvas.configure(background=BACKGROUND)
    for x in range(0, width, 38):
        canvas.create_line(x, 0, x, height, fill=GRID)
    for y in range(0, height, 38):
        canvas.create_line(0, y, width, y, fill=GRID)
    for radius in (.20, .45, .70, .95):
        r_x, r_y = width * .35 * radius, height * .43 * radius
        x, y = width * .57, height * .50
        canvas.create_oval(x-r_x, y-r_y, x+r_x, y+r_y,
                           outline="#18374c", width=1)
    canvas.create_text(20, 17, text="NEUROGENESIS  /  LIF NEURAL FABRIC",
                       fill="#e5f5ff", anchor="nw", font=("Consolas", 12, "bold"))
    fresh = frame.step > 0 and 0 <= event_age < .85
    canvas.create_text(width-18, 20,
                       text="● ZMIANA STANU" if fresh else "○ OCZEKIWANIE NA KROK",
                       fill="#f4bd69" if fresh else "#6e8ba0",
                       anchor="ne", font=("Consolas", 10, "bold"))
    canvas.create_text(20, 46,
                       text=(f"KROK {frame.step}    NEURONY {frame.neurons}    "
                             f"SY NAPSY {frame.synapses}".replace("SY NAPSY", "SYNAPSY")),
                       fill="#8dbfda", anchor="nw", font=("Consolas", 10))
    pts = positions(frame, width, height)
    by_id = {n.index: n for n in frame.nodes}
    opacity = max(0., min(1., 1 - event_age/.85)) if fresh else 0.
    for edge in frame.edges:
        if edge.pre not in pts or edge.post not in pts:
            continue
        x1, y1 = pts[edge.pre]
        x2, y2 = pts[edge.post]
        active = fresh and by_id[edge.pre].spiked
        weight = max(.1, min(1., edge.weight / 1.5))
        shade = "#52c8f8" if active else (LINK if weight >= .45 else QUIET)
        canvas.create_line(x1, y1, x2, y2, fill=shade,
                           width=2 if active else 1)
        if active:
            # Event-attached marker is a **visual representation**, not a
            # measured axonal travel time or additional computed spikes.
            fraction = (1 - opacity)
            px = x1 + (x2-x1)*fraction
            py = y1 + (y2-y1)*fraction
            canvas.create_oval(px-3, py-3, px+3, py+3,
                               fill="#f7bd71", outline="")
    for node in frame.nodes:
        x, y = pts[node.index]
        active = fresh and node.spiked
        intensity = max(0., min(1., node.trace / 5.0))
        radius = 4 + 3 * intensity
        base = SPIKE if active else INPUT if node.is_input else NEURON
        if active:
            canvas.create_oval(x-15, y-15, x+15, y+15,
                               outline="#795b3e", width=2)
            canvas.create_oval(x-9, y-9, x+9, y+9,
                               outline="#b38d4f", width=2)
        elif intensity >= .3:
            canvas.create_oval(x-10, y-10, x+10, y+10,
                               outline="#22475d", width=1)
        canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                           fill=base if intensity > .05 or active or node.is_input else "#365b6d",
                           outline="#b8f8ff" if active else "")
    canvas.create_text(18, height-60,
                       text=(f"IMPULSY W KROKU: {frame.last_spikes}    RAZEM: {frame.total_spikes}"
                             f"    WZROST: +{frame.grown}    PRZYCINANIE: -{frame.pruned}"),
                       fill="#a5dbe8", anchor="nw", font=("Consolas", 10))
    canvas.create_text(18, height-37,
                       text=(f"NOWOŚĆ: {frame.novelty:.3f}    "
                             f"PRÓBA ENERGII (SUMA): {frame.energy_proxy:.1f}    "
                             f"WIDOCZNE: {len(frame.nodes)}/{frame.neurons} · "
                             f"{len(frame.edges)}/{frame.synapses}"),
                       fill="#8fb4ca", anchor="nw", font=("Consolas", 9))
    canvas.create_text(width-18, height-12,
                       text="BŁYSK = OSTATNI ZAPISANY IMPULS · POZYCJA I DROGA: WIZUALIZACJA",
                       fill="#6d8299", anchor="se", font=("Consolas", 8))

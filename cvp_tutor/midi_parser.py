from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import mido
from loguru import logger

from .models import MidiEvent, MidiPart


def load_midi(path: Path) -> Tuple[List[MidiPart], List[MidiEvent], float]:
    """Load a MIDI file and return parts, sorted events, and total length seconds."""
    mid = mido.MidiFile(path)
    parts: List[MidiPart] = []
    events: List[MidiEvent] = []
    total_time = 0.0

    for ti, track in enumerate(mid.tracks):
        abs_time = 0.0
        note_count = 0
        channel_guess = None
        for msg in track:
            abs_time += msg.time
            if msg.type in {"note_on", "note_off"}:
                channel_guess = getattr(msg, "channel", None)
                note_count += 1
                events.append(MidiEvent(time=abs_time, message=msg, track_index=ti, channel=channel_guess))
        parts.append(
            MidiPart(
                name=track.name if hasattr(track, "name") else f"Track {ti}",
                channel=channel_guess,
                track_index=ti,
                note_count=note_count,
            )
        )
        total_time = max(total_time, abs_time)

    events.sort(key=lambda e: e.time)
    logger.info(f"Loaded MIDI: {path} | tracks={len(parts)} events={len(events)} length={total_time:.2f}s")
    return parts, events, total_time


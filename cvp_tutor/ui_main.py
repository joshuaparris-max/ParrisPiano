from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import List, Optional, Tuple

import mido
from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .midi_engine import MidiEngine
from .midi_parser import load_midi
from .models import MidiEvent, MidiPart
from .tutor_engine import TutorEngine


def _clamp_note(value: int) -> int:
    return max(0, min(127, value))


class MainWindow(QMainWindow):
    status_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CVP Tutor")
        self.resize(1000, 620)
        self.engine = MidiEngine()
        self.tutor = TutorEngine()
        self.midi_file: Optional[Path] = None
        self.parts: List[MidiPart] = []
        self.events: List[MidiEvent] = []
        self.total_time: float = 0.0
        self.play_thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.loop_start = 0.0
        self.loop_end: Optional[float] = None
        self.learning_channel: Optional[int] = None
        self.learning_track: Optional[int] = None

        self._build_ui()
        self.status_changed.connect(self._update_status)
        self.refresh_devices(auto_select=True)

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout()

        # Devices
        devices_box = QGroupBox("MIDI Devices")
        d_layout = QGridLayout()
        self.in_combo = QComboBox()
        self.out_combo = QComboBox()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(lambda: self.refresh_devices(auto_select=False))
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_devices)
        test_btn = QPushButton("Test Tone")
        test_btn.clicked.connect(self.test_tone)

        d_layout.addWidget(QLabel("Input"), 0, 0)
        d_layout.addWidget(self.in_combo, 0, 1)
        d_layout.addWidget(QLabel("Output"), 1, 0)
        d_layout.addWidget(self.out_combo, 1, 1)
        d_layout.addWidget(refresh_btn, 0, 2)
        d_layout.addWidget(connect_btn, 1, 2)
        d_layout.addWidget(test_btn, 0, 3, 2, 1)
        devices_box.setLayout(d_layout)

        # File controls
        file_box = QGroupBox("Song")
        f_layout = QGridLayout()
        self.file_label = QLabel("No file loaded")
        self.learning_part_combo = QComboBox()
        self.learning_part_combo.currentIndexChanged.connect(self._part_changed)
        open_btn = QPushButton("Open MIDI")
        open_btn.clicked.connect(self.open_file)
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.start_playback)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_playback)

        self.tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self.tempo_slider.setMinimum(50)
        self.tempo_slider.setMaximum(125)
        self.tempo_slider.setValue(100)
        self.tempo_label = QLabel("Tempo 1.00x")
        self.tempo_slider.valueChanged.connect(self._tempo_changed)

        self.transpose_slider = QSlider(Qt.Orientation.Horizontal)
        self.transpose_slider.setMinimum(-12)
        self.transpose_slider.setMaximum(12)
        self.transpose_slider.setValue(0)
        self.transpose_label = QLabel("Transpose 0")
        self.transpose_slider.valueChanged.connect(self._transpose_changed)

        self.loop_start_spin = QDoubleSpinBox()
        self.loop_start_spin.setRange(0, 3600)
        self.loop_start_spin.setDecimals(2)
        self.loop_end_spin = QDoubleSpinBox()
        self.loop_end_spin.setRange(0, 3600)
        self.loop_end_spin.setDecimals(2)
        self.loop_end_spin.setSpecialValueText("0 = end")
        loop_label = QLabel("Loop start/end (s)")

        self.tutor_toggle = QCheckBox("Tutor (wait for you to play Learning Part)")
        self.tutor_toggle.setChecked(True)

        f_layout.addWidget(open_btn, 0, 0)
        f_layout.addWidget(self.file_label, 0, 1, 1, 3)
        f_layout.addWidget(QLabel("Learning Part"), 1, 0)
        f_layout.addWidget(self.learning_part_combo, 1, 1)
        f_layout.addWidget(self.play_btn, 2, 0)
        f_layout.addWidget(self.stop_btn, 2, 1)
        f_layout.addWidget(self.tutor_toggle, 2, 2, 1, 2)
        f_layout.addWidget(self.tempo_label, 3, 0)
        f_layout.addWidget(self.tempo_slider, 3, 1, 1, 3)
        f_layout.addWidget(self.transpose_label, 4, 0)
        f_layout.addWidget(self.transpose_slider, 4, 1, 1, 3)
        f_layout.addWidget(loop_label, 5, 0)
        f_layout.addWidget(self.loop_start_spin, 5, 1)
        f_layout.addWidget(self.loop_end_spin, 5, 2)
        file_box.setLayout(f_layout)

        # Status
        self.status = QLabel("Ready")

        layout.addWidget(devices_box)
        layout.addWidget(file_box)
        layout.addWidget(self.status)
        root.setLayout(layout)
        self.setCentralWidget(root)

    def refresh_devices(self, auto_select: bool = True) -> None:
        self.in_combo.clear()
        self.out_combo.clear()
        inputs = self.engine.list_inputs()
        outputs = self.engine.list_outputs()
        self.in_combo.addItems(inputs)
        self.out_combo.addItems(outputs)
        if auto_select:
            self._auto_select(inputs, outputs)

    def _auto_select(self, inputs: List[str], outputs: List[str]) -> None:
        def pick(names: List[str]) -> int:
            for i, name in enumerate(names):
                if "CVP-301" in name or "Yamaha" in name:
                    return i
            return 0 if names else -1

        in_idx = pick(inputs)
        out_idx = pick(outputs)
        if in_idx >= 0:
            self.in_combo.setCurrentIndex(in_idx)
        if out_idx >= 0:
            self.out_combo.setCurrentIndex(out_idx)

    def connect_devices(self) -> None:
        input_name = self.in_combo.currentText() or None
        output_name = self.out_combo.currentText() or None
        self.engine.open_ports(input_name, output_name)
        self.status.setText(f"Connected IN={input_name or 'None'} OUT={output_name or 'None'}")

    def test_tone(self) -> None:
        ch = 0
        self.engine.send_test_tone(channel=ch)

    def open_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MIDI", "", "MIDI Files (*.mid *.midi)")
        if not file_path:
            return
        self.load_file(Path(file_path))

    def load_file(self, path: Path) -> None:
        self.midi_file = path
        self.parts, self.events, self.total_time = load_midi(path)
        self.file_label.setText(f"{path.name} ({self.total_time:.1f}s)")
        self.learning_part_combo.clear()
        for idx, part in enumerate(self.parts):
            ch = f"ch {part.channel}" if part.channel is not None else "ch ?"
            self.learning_part_combo.addItem(f"{idx}: {part.name} ({ch}) notes={part.note_count}", userData=part)
        if self.parts:
            self.learning_part_combo.setCurrentIndex(0)
            self._part_changed(0)

    def _part_changed(self, index: int) -> None:
        part: MidiPart = self.learning_part_combo.itemData(index)
        if not part:
            return
        self.learning_channel = part.channel
        self.learning_track = part.track_index

    def _tempo_changed(self, value: int) -> None:
        self.tempo_label.setText(f"Tempo {value/100:.2f}x")

    def _transpose_changed(self, value: int) -> None:
        self.transpose_label.setText(f"Transpose {value:+d}")

    def start_playback(self) -> None:
        if not self.events:
            self.status.setText("Load a MIDI file first.")
            return
        if self.play_thread and self.play_thread.is_alive():
            self.status.setText("Already playing.")
            return
        self.stop_flag.clear()
        self.play_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.play_thread.start()

    def stop_playback(self) -> None:
        self.stop_flag.set()
        self.status.setText("Stopped.")

    def _playback_loop(self) -> None:
        tempo_mult = self.tempo_slider.value() / 100.0
        transpose = self.transpose_slider.value()
        tutor_on = self.tutor_toggle.isChecked()
        loop_start = self.loop_start_spin.value()
        loop_end = self.loop_end_spin.value() or None

        chords = []
        if tutor_on:
            chords = self.tutor.build_expected(self.events, self.learning_channel, self.learning_track)
        chord_idx = 0

        start_wall = time.perf_counter()
        last_event_time = 0.0
        for ev in self.events:
            if self.stop_flag.is_set():
                break
            if ev.time < loop_start:
                continue
            if loop_end and ev.time > loop_end:
                break

            target_time = start_wall + (ev.time - loop_start) / tempo_mult
            while not self.stop_flag.is_set() and time.perf_counter() < target_time:
                time.sleep(0.001)

            msg = ev.message.copy()
            if msg.type in {"note_on", "note_off"} and transpose:
                msg.note = _clamp_note(msg.note + transpose)

            is_learning_part = (self.learning_channel is None or msg.channel == self.learning_channel) and (
                self.learning_track is None or ev.track_index == self.learning_track
            )

            if tutor_on and is_learning_part and msg.type == "note_on" and chord_idx < len(chords):
                expected = chords[chord_idx]
                chord_idx += 1
                matched = self.engine.wait_for_notes(expected.notes, timeout=10, strict=self.tutor.strict)
                status = "matched" if matched else "timeout"
                self.status_changed.emit(f"Tutor: expected {expected.notes} -> {status}")
                continue  # do not play the learning part automatically

            self.engine.send(msg)
            last_event_time = ev.time

        self.status_changed.emit("Playback finished.")

    def _update_status(self, text: str) -> None:
        self.status.setText(text)


def run() -> None:
    logger.info("Starting CVP Tutor UI")
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":  # pragma: no cover
    run()


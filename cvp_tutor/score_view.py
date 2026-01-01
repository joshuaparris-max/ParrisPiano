from __future__ import annotations

from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView


class ScoreView(QWidget):
    """Embeds a PDF score via WebEngine."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.view = QWebEngineView()
        self.label = QLabel("No score loaded")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def load_pdf(self, path: Path) -> None:
        if not path.exists():
            self.label.setText("Score PDF not found.")
            return
        self.view.load(path.as_uri())
        self.label.setText(f"Score: {path.name}")

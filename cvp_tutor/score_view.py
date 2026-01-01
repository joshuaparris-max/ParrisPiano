from __future__ import annotations

from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

# Lazy import to avoid crashing if WebEngine is missing
try:  # pragma: no cover
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except Exception as exc:  # pragma: no cover
    QWebEngineView = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class ScoreView(QWidget):
    """Embeds a PDF score via WebEngine."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.label = QLabel()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        if QWebEngineView is None:
            self.label.setText(f"Score view unavailable: { _IMPORT_ERROR }")
            layout.addWidget(self.label)
            self.view = None
        else:
            self.view = QWebEngineView()
            self.label.setText("No score loaded")
            layout.addWidget(self.view)
            layout.addWidget(self.label)
        self.setLayout(layout)

    def load_pdf(self, path: Path) -> None:
        if not path.exists():
            self.label.setText("Score PDF not found.")
            return
        if self.view is None:
            self.label.setText("Score view unavailable (WebEngine import failed).")
            return
        self.view.load(path.as_uri())
        self.label.setText(f"Score: {path.name}")

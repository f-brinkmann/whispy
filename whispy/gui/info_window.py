from __future__ import annotations

import math
import sys
from typing import Optional

from PyQt6.QtCore import QEventLoop, Qt
from PyQt6.QtGui import QCloseEvent, QColor, QFont, QTextDocument
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


# Module-level QApplication reference — kept alive for the process lifetime so
# that constructing and destroying InfoWindow instances multiple times (e.g.
# in a notebook) never leaves Qt without an application instance.
_qapp: Optional[QApplication] = None

# Module-level registry of top-level InfoWindows that are not stored by the user.
# This keeps them alive so they don't get garbage collected before the user closes them.
_orphaned_windows: list[InfoWindow] = []


class InfoWindow(QWidget):

    def __init__(
        self,
        info_text: str,
        fontsize: int = 12,
        fontcolor: str = "#FFFFFF",
        minimum_width: int=320,
        block_until_closed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:
        # QApplication must exist before any QWidget is constructed.
        # sys.argv[:1] avoids passing Jupyter/IPython kernel arguments to Qt.
        global _qapp
        if QApplication.instance() is None:
            _qapp = QApplication(sys.argv[:1])

        # When running inside an IPython kernel (e.g. VS Code interactive
        # window) enable Qt6 GUI integration so the event loop is active.
        try:
            from IPython import get_ipython
            ip = get_ipython()
            if ip is not None:
                ip.enable_gui('qt6')
        except Exception:
            pass

        super().__init__(parent)
        self.setWindowTitle("")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self._fontsize = max(1, int(fontsize))
        self._minimum_width = max(1, int(minimum_width))
        self._wait_loop: Optional[QEventLoop] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.info_label = QLabel(self._format_markdown(info_text), self)
        self.info_label.setTextFormat(Qt.TextFormat.MarkdownText)
        self.info_label.setWordWrap(False)
        self.info_label.setFont(QFont("Helvetica", self._fontsize))
        self.info_label.setStyleSheet(f"color: {QColor(fontcolor).name()};")

        layout.addWidget(self.info_label)

        controls_layout = QHBoxLayout()
        controls_layout.addStretch(1)

        self.continue_button = QPushButton("Continue", self)
        self._setup_control_button(self.continue_button, self._fontsize)
        self.continue_button.clicked.connect(self.close)

        controls_layout.addWidget(self.continue_button)
        layout.addLayout(controls_layout)

        self._resize_to_content()
        self.show()
        self.raise_()
        self.activateWindow()

        # If this window has no parent, register it globally to prevent garbage collection
        if parent is None:
            _orphaned_windows.append(self)

        if block_until_closed:
            self.wait_until_closed()

    @staticmethod
    def _format_markdown(text: str) -> str:
        return text.replace("\n", "  \n")

    def _resize_to_content(self) -> None:
        doc = QTextDocument()
        doc.setDefaultFont(self.info_label.font())
        doc.setMarkdown(self.info_label.text())
        doc.adjustSize()

        # QLabel and QTextDocument can disagree slightly for markdown layout.
        # Use the larger size to avoid clipping text.
        self.info_label.adjustSize()
        label_hint = self.info_label.sizeHint()

        text_width = max(math.ceil(doc.idealWidth()), label_hint.width())
        text_height = max(math.ceil(doc.size().height()), label_hint.height())

        margins = self.layout().contentsMargins()
        spacing = self.layout().spacing()
        button_width = self.continue_button.width()
        button_height = self.continue_button.height()

        width = max(text_width, button_width) + margins.left() + margins.right() + 8
        height = text_height + button_height + margins.top() + margins.bottom() + spacing + 8
        self.setFixedSize(max(self._minimum_width, width), max(30, height))

    def wait_until_closed(self) -> None:
        if not self.isVisible():
            return

        if self._wait_loop is None:
            self._wait_loop = QEventLoop(self)

        self._wait_loop.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._wait_loop is not None and self._wait_loop.isRunning():
            self._wait_loop.quit()
        # Remove from orphaned windows registry if present
        if self in _orphaned_windows:
            _orphaned_windows.remove(self)
        super().closeEvent(event)

    @staticmethod
    def _setup_control_button(button: QPushButton, button_fontsize: int) -> None:
        font_size = max(1, int(button_fontsize))
        font = QFont("Helvetica", font_size, QFont.Weight.Normal)
        button.setFont(font)
        hint = button.sizeHint()
        width = hint.width() + max(6, int(font_size * 0.5))
        height = hint.height() + max(4, int(font_size * 0.3))
        button.setFixedSize(width, height)

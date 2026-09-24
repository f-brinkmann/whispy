import pytest
from PyQt6.QtGui import QTextDocument

from whispy.ui.base import ensure_qapplication
from whispy.utils._utils import format_markdown


def test_format_markdown_keeps_hard_line_breaks() -> None:
    text = "Line A\nLine B"
    assert format_markdown(text) == "Line A  \nLine B"


def test_format_markdown_adds_spacer_for_spaces_only_separator_line() -> None:
    text = "Line A\n   \nLine B"
    assert format_markdown(text) == "Line A  \n&nbsp;  \nLine B"


def test_format_markdown_preserves_markdown_content() -> None:
    text = "Line A\n**Bold**\nLine B"
    assert format_markdown(text) == "Line A  \n**Bold**  \nLine B"


def test_format_markdown_keeps_list_item_continuation_plain() -> None:
    text = "- Bullet point\nSome text."
    assert format_markdown(text) == "- Bullet point\n\nSome text."


def test_format_markdown_keeps_regular_list_items() -> None:
    text = "- Item A\n- Item B"
    assert format_markdown(text) == "- Item A  \n- Item B"


def test_format_markdown_ends_list_before_blank_line_spacer() -> None:
    text = "- Item A\n- Item B\n\nParagraph"
    assert format_markdown(text) == "- Item A  \n- Item B\n\n&nbsp;  \nParagraph"


@pytest.mark.parametrize("items", ["- Item A\n- Item B", "1. Item A\n2. Item B"])
def test_paragraph_after_list_renders_outside_the_list(items: str) -> None:
    ensure_qapplication()
    doc = QTextDocument()
    doc.setMarkdown(format_markdown(f"{items}\n\nAfter the list.\n\nLast line."))

    in_list = {}
    block = doc.begin()
    while block.isValid():
        if block.text().strip():
            in_list[block.text().strip()] = block.textList() is not None
        block = block.next()

    assert in_list["Item B"]
    assert not in_list["After the list."]
    assert not in_list["Last line."]

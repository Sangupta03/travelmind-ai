from core.markdown_render import render_ai_reasoning


def test_empty_text_returns_empty_string():
    assert render_ai_reasoning("") == ""
    assert render_ai_reasoning(None) == ""


def test_bold_and_italic_render():
    html = render_ai_reasoning("Some **bold text** and *italic text*.")
    assert "<strong>bold text</strong>" in html
    assert "<em>italic text</em>" in html


def test_headers_render():
    html = render_ai_reasoning("### A subheading")
    assert "<h3>A subheading</h3>" in html


def test_list_immediately_after_a_label_line_still_renders_as_a_list():
    text = "Budget-Friendly Selections:\n* Flights: 7702\n* Hotel: 10660"
    html = render_ai_reasoning(text)
    assert "<ul>" in html
    assert "<li>Flights: 7702</li>" in html
    assert "<li>Hotel: 10660</li>" in html
    # the literal asterisk should not leak into the rendered output
    assert "* Flights" not in html


def test_nested_list_renders_as_nested_ul():
    text = "Costs:\n*   Flights:\n    *   Airline: AI\n    *   Price: 7702\n*   Total: 7702"
    html = render_ai_reasoning(text)
    assert html.count("<ul>") == 2
    assert "<li>Airline: AI</li>" in html


def test_blank_line_already_present_is_left_working():
    text = "Header:\n\n* item one\n* item two"
    html = render_ai_reasoning(text)
    assert "<li>item one</li>" in html
    assert "<li>item two</li>" in html

#!/usr/bin/env python3

"""Test script to verify TUI components are rendering correctly"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, RichLog, Label, Input, Button


class TestTUIApp(App):
    """Test TUI to verify components render correctly"""

    CSS_PATH = "chat_tui.css"

    def __init__(self):
        super().__init__()
        self._load_css()

    def _load_css(self):
        """Load CSS from external file"""
        css_path = Path(__file__).parent / self.CSS_PATH
        self.CSS = css_path.read_text()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        # Topic container
        with Container(id="topic-container"):
            yield Label("Test Topic Display", id="topic-label")

        # Chat container
        with Container(id="chat-container"):
            yield RichLog(id="chat-log", highlight=True, markup=True)

        # Input container with explicit button
        with Horizontal(id="input-container"):
            yield Input(placeholder="Enter test topic...", id="topic-input")
            yield Button("Start", variant="primary", id="start-button")

        # Status bar
        yield Label("Status: Test Mode", id="status")

        yield Footer()

    async def on_mount(self) -> None:
        """Called when app starts"""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write("Test TUI Application")
        chat_log.write("================")
        chat_log.write("")
        chat_log.write("✅ Chat log is working")
        chat_log.write("✅ Input field should be visible below")
        chat_log.write("✅ Start button should be visible to the right of input")
        chat_log.write("")

        # Verify button exists
        try:
            button = self.query_one("#start-button", Button)
            chat_log.write(f"✅ Button found: '{button.label}' variant='{button.variant}'")
        except Exception as e:
            chat_log.write(f"❌ Button error: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(f"✅ Button clicked: {event.button.label}")


if __name__ == "__main__":
    app = TestTUIApp()
    app.run()

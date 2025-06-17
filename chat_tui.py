#!/usr/bin/env python3

import json
import requests
import time
import os
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, RichLog, Label, Input, Button
from textual.message import Message
from textual import work
from rich.text import Text


class OllamaBot:
    def __init__(self, name: str, ollama_url: str, model: str, personality: str):
        self.name = name
        self.ollama_url = ollama_url
        self.model = model
        self.personality = personality

    async def generate_response_async(self, system_prompt: str, conversation_history: str, timeout: int = 30) -> str:
        """Generate a response from the bot using Ollama API (async version)"""
        full_prompt = f"{system_prompt}\n\nYour personality: {self.personality}\n\nConversation so far:\n{conversation_history}\n\n{self.name}:"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False  # Non-streaming for simplicity in async
        }

        try:
            # Run the blocking request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=timeout
                )
            )
            response.raise_for_status()

            data = response.json()
            return data.get('response', '[No response]').strip()
        except requests.exceptions.RequestException:
            return f"[Error: Could not get response from {self.name}]"


class ChatMessage(Message):
    """Message to add chat content"""
    def __init__(self, bot_name: str, content: str) -> None:
        self.bot_name = bot_name
        self.content = content
        super().__init__()


class ChatTUI(App):
    """TUI for AI Round-Table Discussion"""

    CSS_PATH = "chat_tui.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("s", "toggle_scroll", "Auto-scroll"),
        ("p", "pause_resume", "Pause/Resume"),
        ("u", "update_topic", "Update Topic"),
    ]

    def __init__(self, config_path: str = "config.json"):
        super().__init__()
        self.config = self.load_config(config_path)
        self.bots = self.initialize_bots()
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = "chat_logs"
        self.ensure_log_directory()
        self.log_file_path = os.path.join(self.log_dir, f"session_{self.session_id}.txt")
        self.topic = ""
        self.bot_index = 0
        self._is_running = False
        self._is_paused = False
        self.auto_scroll = True
        self._load_css()

    def _load_css(self):
        """Load CSS from external file"""
        css_path = Path(__file__).parent / self.CSS_PATH
        self.CSS = css_path.read_text()

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.exit(message=f"Error: Configuration file '{config_path}' not found.")
            return {}
        except json.JSONDecodeError:
            self.exit(message=f"Error: Invalid JSON in configuration file '{config_path}'.")
            return {}

    def initialize_bots(self) -> List[OllamaBot]:
        """Initialize all bots from configuration"""
        bots = []
        for bot_config in self.config["bots"]:
            bot = OllamaBot(
                name=bot_config["name"],
                ollama_url=bot_config["ollama_url"],
                model=bot_config["model"],
                personality=bot_config["personality"]
            )
            bots.append(bot)
        return bots

    def ensure_log_directory(self):
        """Ensure the log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_message(self, bot_name: str, message: str, is_topic: bool = False):
        """Log a message to the session file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            if is_topic:
                f.write(f"{'='*80}\n")
                f.write(f"Session Started: {timestamp}\n")
                f.write(f"Topic: {message}\n")
                f.write(f"{'='*80}\n\n")
            else:
                f.write(f"[{timestamp}] {bot_name}:\n")
                f.write(f"{message}\n")
                f.write(f"{'-'*40}\n\n")

    def get_conversation_context(self) -> str:
        """Get the conversation history as a formatted string"""
        if not self.conversation_history:
            return "No previous conversation."

        context = ""
        for entry in self.conversation_history[-10:]:  # Keep last 10 messages for context
            context += f"{entry['bot']}: {entry['message']}\n"
        return context

    def add_to_history(self, bot_name: str, message: str):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "bot": bot_name,
            "message": message,
            "timestamp": time.time()
        })
        # Log the message to file (skip system messages)
        if bot_name != "Moderator":
            self.log_message(bot_name, message)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        # Topic container
        with Container(id="topic-container"):
            yield Label("No topic set", id="topic-label")

        # Chat container
        with Container(id="chat-container"):
            yield RichLog(id="chat-log", highlight=True, markup=True, auto_scroll=True, wrap=True)

        # Input container
        with Horizontal(id="input-container"):
            yield Input(placeholder="Enter discussion topic and press Start...", id="topic-input")
            yield Button("Start", variant="primary", id="start-button")

        # Status bar
        yield Label(f"Session: {self.session_id} | Status: Ready", id="status")

        yield Footer()

    async def on_mount(self) -> None:
        """Called when app starts"""
        # Display bot information in the log
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(Text("🎪 AI Round-Table Discussion", style="bold magenta"))
        chat_log.write("")
        chat_log.write("Participants:")
        for bot in self.bots:
            chat_log.write(f"  🤖 {bot.name} ({bot.model}) - {bot.personality[:50]}...")
        chat_log.write("")
        chat_log.write(f"💾 Session ID: {self.session_id}")
        chat_log.write(f"📁 Logs directory: {self.log_dir}/")
        chat_log.write("")
        chat_log.write(Text("➡️  Enter a topic below and press Enter or click 'Start' to begin", style="bold yellow"))
        chat_log.write("")
        chat_log.write(Text("Keyboard shortcuts: [q]uit, [s]croll toggle, [p]ause/resume, [u]pdate topic", style="dim"))
        chat_log.write("")

        # Focus on the input field
        self.query_one("#topic-input", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "start-button":
            await self.toggle_discussion()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field"""
        if event.input.id == "topic-input":
            if self._is_paused:
                await self.add_topic_update()
            elif not self._is_running:
                await self.toggle_discussion()

    async def toggle_discussion(self) -> None:
        """Toggle the discussion on/off"""
        if not self._is_running and not self._is_paused:
            topic_input = self.query_one("#topic-input", Input)
            topic = topic_input.value.strip()

            if topic:
                self.topic = topic
                topic_input.disabled = True
                start_button = self.query_one("#start-button", Button)
                start_button.label = "Stop"
                start_button.variant = "error"
                self.start_discussion()
            else:
                chat_log = self.query_one("#chat-log", RichLog)
                chat_log.write(Text("⚠️ Please enter a topic first!", style="yellow"))
        elif self._is_running:
            self.stop_discussion()
            start_button = self.query_one("#start-button", Button)
            start_button.label = "Start"
            start_button.variant = "primary"
            topic_input = self.query_one("#topic-input", Input)
            topic_input.disabled = False

    def start_discussion(self) -> None:
        """Start the discussion"""
        self._is_running = True
        self._is_paused = False

        # Update topic label
        topic_label = self.query_one("#topic-label", Label)
        topic_label.update(f"Topic: {self.topic}")

        # Clear and update chat log only if this is a new discussion
        chat_log = self.query_one("#chat-log", RichLog)
        if not self.conversation_history:
            chat_log.clear()
            chat_log.write(Text(f"🎯 Discussion Topic: {self.topic}", style="bold cyan"))
            chat_log.write("")
            # Log the topic
            self.log_message("", self.topic, is_topic=True)
            # Add topic to conversation history
            self.add_to_history("Moderator", f"Today's discussion topic is: {self.topic}")
        else:
            # Resuming after pause
            chat_log.write("")
            chat_log.write(Text("▶️ Discussion resumed", style="green"))
            chat_log.write("")

        # Update status
        self.update_status("Discussion in progress...")

        # Start the discussion worker
        self.run_discussion_worker()

    def stop_discussion(self, pause_only: bool = False) -> None:
        """Stop the discussion"""
        self._is_running = False
        self._is_paused = pause_only

        if pause_only:
            self.update_status("Discussion paused")
            chat_log = self.query_one("#chat-log", RichLog)
            chat_log.write("")
            chat_log.write(Text("⏸️ Discussion paused. Enter new topic direction below or press 'p' to resume.", style="yellow"))
            # Enable input for topic updates
            topic_input = self.query_one("#topic-input", Input)
            topic_input.disabled = False
            topic_input.placeholder = "Add new topic direction or press 'p' to resume..."
            topic_input.value = ""
            topic_input.focus()
        else:
            self.update_status("Discussion stopped")
            chat_log = self.query_one("#chat-log", RichLog)
            chat_log.write("")
            chat_log.write(Text("⏹️ Discussion stopped by user.", style="yellow"))
            chat_log.write(f"💾 Chat log saved to: {self.log_file_path}")

    def update_status(self, message: str) -> None:
        """Update the status bar"""
        status = self.query_one("#status", Label)
        status.update(f"Session: {self.session_id} | Status: {message}")

    @work(exclusive=True)
    async def run_discussion_worker(self) -> None:
        """Run the discussion in a worker"""
        chat_log = self.query_one("#chat-log", RichLog)
        timeout = self.config.get("response_timeout", 30)

        while self._is_running:
            bot = self.bots[self.bot_index]

            # Show which bot is thinking
            timestamp = datetime.now().strftime("%H:%M:%S")
            chat_log.write(f"[dim]{timestamp}[/dim] [bold green]{bot.name}[/bold green] is thinking...")

            # Get conversation context
            context = self.get_conversation_context()

            # Generate response
            start_time = time.time()
            response = await bot.generate_response_async(
                self.config["system_prompt"],
                context,
                timeout
            )
            response_time = time.time() - start_time

            # Clear the "thinking" message and show the actual response
            # Write bot name and response on separate lines for better wrapping
            chat_log.write(f"[dim]{timestamp}[/dim] [bold green]{bot.name}:[/bold green]")
            chat_log.write(response)
            chat_log.write(f"[dim]   (Response time: {response_time:.1f}s)[/dim]")
            chat_log.write("")

            # Add to conversation history (this also logs to file)
            self.add_to_history(bot.name, response)

            # Move to next bot (circular)
            self.bot_index = (self.bot_index + 1) % len(self.bots)

            # Small delay between responses
            await asyncio.sleep(1)

            # Check if we should stop
            if not self._is_running:
                break

    async def action_quit(self) -> None:
        """Quit the application"""
        if self._is_running:
            self.stop_discussion()
        self.exit()

    async def action_toggle_scroll(self) -> None:
        """Toggle auto-scroll"""
        self.auto_scroll = not self.auto_scroll
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.auto_scroll = self.auto_scroll
        self.notify(f"Auto-scroll: {'ON' if self.auto_scroll else 'OFF'}")

    async def action_pause_resume(self) -> None:
        """Pause or resume the discussion"""
        if self.topic:
            if self._is_running:
                self.stop_discussion(pause_only=True)
            else:
                self.start_discussion()

    async def action_update_topic(self) -> None:
        """Focus on input for topic update when paused"""
        if self._is_paused and not self._is_running:
            topic_input = self.query_one("#topic-input", Input)
            topic_input.focus()

            chat_log = self.query_one("#chat-log", RichLog)
            chat_log.write("")
            chat_log.write(Text("💡 Type your topic update in the input field below", style="cyan"))

    async def add_topic_update(self) -> None:
        """Add topic update to the discussion"""
        topic_input = self.query_one("#topic-input", Input)
        update_text = topic_input.value.strip()

        if update_text:
            chat_log = self.query_one("#chat-log", RichLog)
            chat_log.write("")
            chat_log.write(Text(f"📝 Topic Update: {update_text}", style="bold magenta"))

            # Add to conversation history
            self.add_to_history("Moderator", f"Let's expand our discussion to also consider: {update_text}")

            # Log the topic update
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n[{timestamp}] TOPIC UPDATE:\n")
                f.write(f"{update_text}\n")
                f.write(f"{'-'*40}\n\n")

            # Clear and disable input
            topic_input.value = ""
            topic_input.disabled = True
            topic_input.placeholder = "Press 'p' to resume discussion..."

            chat_log.write(Text("✅ Topic update added. Press 'p' to resume discussion.", style="green"))


def main():
    """Main function to run the TUI application"""
    app = ChatTUI()
    app.run()


if __name__ == "__main__":
    main()

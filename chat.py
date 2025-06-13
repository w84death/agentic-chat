#!/usr/bin/env python3

import json
import requests
import time
import sys
from typing import Dict, List, Any

class OllamaBot:
    def __init__(self, name: str, ollama_url: str, model: str, personality: str):
        self.name = name
        self.ollama_url = ollama_url
        self.model = model
        self.personality = personality

    def generate_response_stream(self, system_prompt: str, conversation_history: str, timeout: int = 30):
        """Generate a streaming response from the bot using Ollama API"""
        full_prompt = f"{system_prompt}\n\nYour personality: {self.personality}\n\nConversation so far:\n{conversation_history}\n\n{self.name}:"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True
        }

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=timeout,
                stream=True
            )
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            token = data['response']
                            print(token, end='', flush=True)
                            full_response += token
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue

            return full_response.strip()
        except requests.exceptions.RequestException as e:
            error_msg = f"[Error: Could not get response from {self.name}]"
            print(error_msg)
            return error_msg

class ChatRoom:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.bots = self.initialize_bots()
        self.conversation_history = []

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file '{config_path}'.")
            sys.exit(1)

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

    def print_separator(self):
        """Print a visual separator"""
        print("-" * 80)

    def start_discussion(self, topic: str):
        """Start the round-table discussion"""
        print(f"\n🎯 Discussion Topic: {topic}")
        self.print_separator()
        print("Starting continuous round-table discussion...")
        print("Press Ctrl+D to exit gracefully\n")

        # Add topic to conversation history
        self.add_to_history("Moderator", f"Today's discussion topic is: {topic}")

        rounds = 0
        timeout = self.config.get("response_timeout", 30)

        try:
            while True:
                rounds += 1
                print(f"--- Round {rounds} ---\n")

                for bot in self.bots:
                    print(f"🤖 {bot.name}: ", end='', flush=True)

                    # Get current conversation context
                    context = self.get_conversation_context()

                    # Generate streaming response
                    start_time = time.time()
                    response = bot.generate_response_stream(
                        self.config["system_prompt"],
                        context,
                        timeout
                    )
                    response_time = time.time() - start_time

                    print(f"\n   (Response time: {response_time:.1f}s)")
                    print()

                    # Add to conversation history
                    self.add_to_history(bot.name, response)

                    # Small delay between responses
                    time.sleep(1)

                self.print_separator()

        except EOFError:
            print(f"\n🏁 Discussion completed after {rounds} rounds!")
            print("Thank you for hosting this AI round-table discussion!")
        except KeyboardInterrupt:
            print(f"\n\nDiscussion interrupted after {rounds} rounds. Goodbye!")

def main():
    """Main function to run the chat application"""
    print("=" * 80)
    print("🎪 AI Round-Table Discussion")
    print("=" * 80)
    print()

    # Initialize chat room
    try:
        chat_room = ChatRoom()
    except Exception as e:
        print(f"Error initializing chat room: {e}")
        sys.exit(1)

    # Display bot information
    print("Participants:")
    for bot in chat_room.bots:
        print(f"  🤖 {bot.name} ({bot.model}) - {bot.personality[:50]}...")
    print()

    # Get discussion topic from user
    try:
        topic = input("Enter the discussion topic: ").strip()
        if not topic:
            print("No topic provided. Exiting.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except EOFError:
        print("\nExiting...")
        sys.exit(0)

    # Start the discussion
    try:
        chat_room.start_discussion(topic)
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
import requests
import time
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

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
                        if 'response' in data and data['response']:
                            token = data['response']
                            print(token, end='', flush=True)
                            full_response += token
                        # Only break after we've processed any final response tokens
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue

            # Ensure output is flushed and we have a newline
            print('', flush=True)

            # Small delay to ensure all streaming is complete
            time.sleep(0.1)

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
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = "chat_logs"
        self.ensure_log_directory()
        self.log_file_path = os.path.join(self.log_dir, f"session_{self.session_id}.txt")

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



    def start_discussion(self, topic: str):
        """Start the round-table discussion"""
        print(f"\n🎯 Discussion Topic: {topic}")
        print(f"💾 Logging to: {self.log_file_path}")
        print("Starting continuous discussion...")
        print("Press Ctrl+C to exit\n")

        # Log the topic
        self.log_message("", topic, is_topic=True)

        # Add topic to conversation history
        self.add_to_history("Moderator", f"Today's discussion topic is: {topic}")

        timeout = self.config.get("response_timeout", 30)
        bot_index = 0

        try:
            while True:
                bot = self.bots[bot_index]
                print(f"🤖 {bot.name}: ", end='', flush=True)

                # Get conversation context
                context = self.get_conversation_context()

                # Generate response
                start_time = time.time()
                response = bot.generate_response_stream(
                    self.config["system_prompt"],
                    context,
                    timeout
                )
                response_time = time.time() - start_time

                print(f"   (Response time: {response_time:.1f}s)")

                # Add to conversation history (this also logs to file)
                self.add_to_history(bot.name, response)

                # Move to next bot (circular)
                bot_index = (bot_index + 1) % len(self.bots)

                # Small delay between responses
                time.sleep(1)
                print()  # Add spacing between responses

        except KeyboardInterrupt:
            print(f"\n\nDiscussion interrupted.")
            print(f"💾 Chat log saved to: {self.log_file_path}")
        finally:
            print("Goodbye!")

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

    # Display logging info
    print(f"💾 Session ID: {chat_room.session_id}")
    print(f"📁 Logs directory: {chat_room.log_dir}/")
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

    # Start the discussion
    try:
        chat_room.start_discussion(topic)
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()

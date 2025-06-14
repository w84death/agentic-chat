#!/usr/bin/env python3

import json
import requests
import time
import sys
import subprocess
import os
from typing import Dict, List, Any, Optional, Tuple
import threading
import queue
import concurrent.futures

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
        self.tts_enabled = self.config.get("tts_enabled", True)
        self.tts_voice = self.config.get("tts_voice", "en-US")
        self.tts_speed = self.config.get("tts_speed", 1.0)
        self.tts_queue = queue.Queue()
        self.tts_thread = None
        self.tts_active = False

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



    def speak_text(self, text: str, bot_name: str = ""):
        """Use espeak-ng to speak the given text"""
        if not self.tts_enabled:
            return

        # Clean the text for TTS
        clean_text = text.replace("[Error:", "Error:").replace("]", "").replace("*", "")
        speed = int(150 * self.tts_speed)

        # Use espeak-ng to speak directly
        cmd = [
            "espeak-ng",
            "-v", "en-US",
            "-s", str(speed),
            clean_text
        ]

        subprocess.run(cmd, capture_output=True)

    def tts_worker(self):
        """Worker thread for processing TTS queue"""
        while self.tts_active:
            try:
                # Wait for TTS task with timeout
                task = self.tts_queue.get(timeout=1)
                if task is None:  # Shutdown signal
                    break

                text, bot_name = task
                self.speak_text(text, bot_name)
                self.tts_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n[TTS Error: {e}]")
                self.tts_queue.task_done()

    def queue_tts(self, text: str, bot_name: str = ""):
        """Queue text for TTS playback"""
        if self.tts_enabled and text and not text.startswith("[Error:"):
            self.tts_queue.put((text, bot_name))

    def start_tts_thread(self):
        """Start the TTS worker thread"""
        if self.tts_enabled and not self.tts_active:
            self.tts_active = True
            self.tts_thread = threading.Thread(target=self.tts_worker, daemon=True)
            self.tts_thread.start()

    def stop_tts_thread(self):
        """Stop the TTS worker thread"""
        if self.tts_active:
            self.tts_active = False
            self.tts_queue.put(None)  # Shutdown signal
            if self.tts_thread:
                self.tts_thread.join(timeout=5)

    def wait_for_tts_completion(self):
        """Wait for all queued TTS to complete"""
        if self.tts_enabled:
            self.tts_queue.join()

    def generate_bot_response(self, bot: OllamaBot, context: str, timeout: int) -> Tuple[str, float]:
        """Generate response for a single bot"""
        start_time = time.time()
        response = bot.generate_response_stream(
            self.config["system_prompt"],
            context,
            timeout
        )
        response_time = time.time() - start_time

        # Ensure response is complete before returning
        if response and not response.startswith("[Error:"):
            # Small buffer to ensure streaming is fully complete
            time.sleep(0.2)

        return response, response_time

    def start_discussion(self, topic: str):
        """Start the round-table discussion"""
        print(f"\n🎯 Discussion Topic: {topic}")
        print("Starting continuous discussion...")
        print("Press Ctrl+C to exit\n")

        # Add topic to conversation history
        self.add_to_history("Moderator", f"Today's discussion topic is: {topic}")

        timeout = self.config.get("response_timeout", 30)

        # Start TTS thread
        self.start_tts_thread()

        try:
            # Use ThreadPoolExecutor for continuous parallel generation
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_response = None
                bot_index = 0

                while True:
                    bot = self.bots[bot_index]

                    # Check if we have a pre-generated response
                    if future_response is not None:
                        # Wait for pre-generated response
                        try:
                            response, response_time = future_response.result(timeout=1)
                            print(f"   (Response time: {response_time:.1f}s)")
                        except concurrent.futures.TimeoutError:
                            print(f"   ⚠️  Pre-generation timed out, generating now...")
                            print(f"🤖 {bot.name}: ", end='', flush=True)
                            context = self.get_conversation_context()
                            response, response_time = self.generate_bot_response(bot, context, timeout)
                            print(f"   (Response time: {response_time:.1f}s)")
                    else:
                        # Generate response normally
                        print(f"🤖 {bot.name}: ", end='', flush=True)
                        context = self.get_conversation_context()
                        response, response_time = self.generate_bot_response(bot, context, timeout)
                        print(f"   (Response time: {response_time:.1f}s)")

                    # Add to conversation history
                    self.add_to_history(bot.name, response)

                    # Queue TTS for current response
                    if response and not response.startswith("[Error:"):
                        print("   🔊 Speaking...")
                        self.queue_tts(response, bot.name)

                    # Determine next bot (circular)
                    next_bot_index = (bot_index + 1) % len(self.bots)
                    next_bot = self.bots[next_bot_index]

                    # Start generating next bot's response in parallel
                    print(f"   ⏳ Pre-generating response for {next_bot.name}...")

                    # Get updated context for next bot
                    next_context = self.get_conversation_context()

                    # Submit next generation task
                    future_response = executor.submit(
                        self.generate_bot_response,
                        next_bot,
                        next_context,
                        timeout
                    )

                    # Wait for current TTS to complete before next bot speaks
                    self.wait_for_tts_completion()

                    # Print next bot's name in preparation
                    print(f"\n\n🤖 {next_bot.name}: ", end='', flush=True)

                    # Move to next bot
                    bot_index = next_bot_index

                    # Small delay between bots
                    time.sleep(0.2)

        except KeyboardInterrupt:
            print(f"\n\nDiscussion interrupted. Shutting down gracefully...")
        finally:
            # Stop TTS thread
            self.stop_tts_thread()
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

    # Display TTS status
    if chat_room.tts_enabled:
        print(f"🔊 TTS: Enabled (Voice: {chat_room.tts_voice})")
    else:
        print("🔇 TTS: Disabled")
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

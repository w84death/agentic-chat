# AI Round-Table Discussion

A simple terminal application that hosts a chat between different AI models powered by local Ollama instances. The bots participate in a round-table discussion, taking turns to respond to a topic you provide.

## Features

- 3 AI bots with different personalities (Philosopher, Scientist, Artist)
- Configurable Ollama instances and models
- Round-table discussion format
- Conversation history tracking
- **Text-to-Speech (TTS)** - Uses espeak-ng to read bot responses aloud
- Simple terminal interface

## Prerequisites

1. **Ollama** - Make sure you have Ollama installed and running locally
   - Install from: https://ollama.ai/
   - Start Ollama: `ollama serve`

2. **Required Models** - Pull the models specified in your config:
   ```bash
   ollama pull gemma3:1b-it-qat
   ```

3. **TTS Dependencies** (Optional) - For text-to-speech functionality:
   ```bash
   sudo apt-get install espeak-ng
   ```
   Or for RHEL/CentOS/Fedora:
   ```bash
   sudo dnf install espeak-ng
   ```

4. **Python 3.7+** with pip

Enjoy your AI round-table discussions! 🎪🤖

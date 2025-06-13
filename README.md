# AI Round-Table Discussion

A simple terminal application that hosts a chat between different AI models powered by local Ollama instances. The bots participate in a round-table discussion, taking turns to respond to a topic you provide.

## Features

- 4 AI bots with different personalities (Philosopher, Scientist, Artist, Pragmatist)
- Configurable Ollama instances and models
- Round-table discussion format
- Conversation history tracking
- Simple terminal interface

## Prerequisites

1. **Ollama** - Make sure you have Ollama installed and running locally
   - Install from: https://ollama.ai/
   - Start Ollama: `ollama serve`

2. **Required Models** - Pull the models specified in your config:
   ```bash
   ollama pull llama2
   ollama pull mistral
   ollama pull codellama
   ollama pull neural-chat
   ```

3. **Python 3.7+** with pip

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your bots by editing `config.json`:
   - Adjust `ollama_url` if your Ollama instance runs on a different address
   - Change `model` names to match your available models
   - Customize bot personalities
   - Modify `response_timeout` and `max_rounds` as needed

## Usage

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Run the chat application:
   ```bash
   python chat.py
   ```

3. Enter a discussion topic when prompted

4. Watch the AI bots discuss the topic in rounds

5. Press Enter to continue to the next round, or type 'n' to end the discussion

## Configuration

The `config.json` file contains:

- `system_prompt`: Instructions for all bots about how to behave
- `bots`: Array of bot configurations with:
  - `name`: Display name for the bot
  - `ollama_url`: URL of the Ollama instance
  - `model`: Model name to use
  - `personality`: Character description for the bot
- `response_timeout`: Maximum time to wait for a response (seconds)
- `max_rounds`: Maximum number of discussion rounds

## Example Topics

- "The impact of artificial intelligence on society"
- "Should we colonize Mars?"
- "The future of work in the digital age"
- "Climate change solutions"
- "The ethics of genetic engineering"

## Troubleshooting

- **Connection errors**: Make sure Ollama is running and accessible
- **Model not found**: Ensure the models specified in config.json are pulled with `ollama pull <model>`
- **Slow responses**: Increase `response_timeout` in config.json
- **Keyboard interrupt**: Use Ctrl+C to stop the discussion at any time

## Customization

You can easily customize the application by:
- Adding more bots to the configuration
- Changing bot personalities
- Using different Ollama models
- Adjusting the system prompt
- Modifying response timeouts

Enjoy your AI round-table discussions! 🎪🤖
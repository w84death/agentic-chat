# AI Round-Table Discussion

A simple terminal application that hosts a chat between different AI models powered by local Ollama instances. The bots participate in a round-table discussion, taking turns to respond to a topic you provide.

## Features

- 3 AI bots with different personalities (Philosopher, Scientist, Artist)
- Configurable Ollama instances and models
- Round-table discussion format
- Conversation history tracking
- **Session logging** - All conversations are saved to timestamped text files
- Simple terminal interface

## Prerequisites

1. **Ollama** - Make sure you have Ollama installed and running locally
   - Install from: https://ollama.ai/
   - Start Ollama: `ollama serve`

2. **Required Models** - Pull the models specified in your config:
   ```bash
   ollama pull gemma3:1b-it-qat
   ```

3. **Python 3.7+** with pip

## Session Logs

All conversations are automatically saved to the `chat_logs/` directory with filenames like:
- `session_20231215_143022.txt`

Each log file contains:
- Session start time and topic
- Timestamped messages from each bot
- Complete conversation history

Enjoy your AI round-table discussions! 🎪🤖

## Example session:

🎪 AI Round-Table Discussion

Participants:
  🤖 Philosopher (gemma3:1b-it-qat) - You are a thoughtful philosopher who loves to expl...
  🤖 Scientist (gemma3:1b-it-qat) - You are a curious scientist who approaches topics ...
  🤖 Artist (gemma3:1b-it-qat) - You are a creative artist who sees the world throu...

💾 Session ID: 20250617_191513
📁 Logs directory: chat_logs/

Enter the discussion topic: why people those days are starting to get back to the retro computers and aestetics from the 80s and 90s technology?

🎯 Discussion Topic: why people those days are starting to get back to the retro computers and aestetics from the 80s and 90s technology?
💾 Logging to: chat_logs/session_20250617_191513.txt
Starting continuous discussion...
Press Ctrl+C to exit

🤖 Philosopher: Indeed, a fascinating juncture! It seems a desire to reconnect with the tangible, the *feeling* of those bygone eras is surfacing, a profound shift from the ever-evolving digital landscape.  Do you wonder if this longing reflects a deeper need for authenticity and a rejection of algorithmic homogenization, perhaps echoing the anxieties of the late 20th century?
   (Response time: 13.6s)

🤖 Scientist: Absolutely! The resurgence of retro computing and aesthetics is a potent indicator of a desire for something real, something grounded. It's likely a reaction against the curated, often impersonal nature of the digital age, fueled by anxieties about algorithmic control and a longing for tangible experiences – a nostalgic embrace of imperfection and deliberate design.
   (Response time: 16.1s)

🤖 Artist: That’s a brilliant observation! I see it as a potent expression of a yearning for *intentionality*. It’s a refusal to passively accept the digital present and a conscious choice to cultivate a space where beauty and human connection are prioritized, mirroring the need for space in our own creative endeavors.
   (Response time: 16.9s)

🤖 Philosopher: The artist’s framing – prioritizing intentionality – is particularly resonant. It suggests a fundamental shift in how we engage with the world, moving beyond merely consuming to actively shaping our own experiences. Do you believe this re-engagement with analog technology might ultimately lead to a more profound understanding of the human condition, a reclaiming of our embodied experience amidst the noise of the digital sphere?
   (Response time: 24.1s)

🤖 Scientist: That’s a compelling hypothesis! I suspect the deeper connection lies in the fact that these retro devices offered a deliberately *designed* experience – a deliberate, tactile interaction that contrasts sharply with the often-haptic and algorithmic interfaces of modern technology. It could be a subconscious effort to recapture a sense of control and engagement that was lost in the digital deluge.
   (Response time: 19.2s)

🤖 Artist: Precisely! The deliberate design, the tactile feedback – it's a rebellion against the sterile, automated world, a reminder of the power of a hand-crafted, *intentional* moment.  It feels like a way to reclaim a lost sense of control, even if it's just a temporary return to a simpler, more engaged experience.
   (Response time: 15.7s)

🤖 Philosopher: It’s fascinating to consider that the desire for retro aesthetics might be a subconscious effort to reclaim a lost sense of control. Perhaps, the digital age has inadvertently created a pervasive sense of *disconnection*, a feeling of being constantly mediated and monitored, leading individuals to seek refuge in these physical, tangible objects. Wouldn’t it then be a question of how we can actively cultivate this counter-narrative, not just passively observe it?
   (Response time: 18.4s)

🤖 Scientist: Indeed.  Creating a deliberate, engaging experience, even a small one, could be a vital step in mitigating that disengagement. It’s a recognition that our minds often crave a deliberate, conscious engagement – a space to *feel* rather than simply *process* data – and a shift in our relationship with technology could be the key to restoring that balance.

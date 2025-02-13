# RecluseAI - Open Source Twitter AI Agent

RecluseAI is an intelligent, autonomous Twitter agent that engages with mentions in real time. It can analyze tweets, detect bot activity, and generate human-like responses based on the conversation context. Powered by OpenAI, Redis, LangChain, and Supabase, this AI agent brings interactivity to your Twitter presence while maintaining a unique personality.

## Features

- **Automated Twitter Engagement**: Reads and responds to Twitter mentions.
- **Bot Detection**: Filters out suspicious bot activity before responding.
- **Intelligent Contextual Replies**: Determines whether to reply, retweet, or provide relevant information.
- **Redis-Powered Caching**: Uses Redis for efficient data retrieval and rate-limiting.
- **Database Tracking**: Logs interactions in Supabase for persistence.

## Tech Stack

- **Python 3.9+**
- **Redis (asyncio)**
- **OpenAI API**
- **LangChain**
- **Supabase**
- **Heroku (Deployment)**

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.9+
- Redis
- Twitter API Credentials
- OpenAI API Key
- Supabase Account & Credentials

### Setup

\`\`\`bash
# Clone the repository
git clone https://github.com/recluseai/recluse-ai-agent.git
cd recluse-ai-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys and database credentials
\`\`\`

## Usage

### Running the AI Agent

\`\`\`bash
python main.py
\`\`\`

The agent will continuously check for Twitter mentions, analyze interactions, and respond accordingly.

## How It Works

1. **Fetching Mentions**: The agent reads the latest mentions of the configured Twitter handle.
2. **Bot Detection**: Uses OpenAI to determine if the mention is from a bot.
3. **Understanding Context**: Identifies whether the mention requires a reply, retweet, or search query.
4. **Generating a Response**: Uses AI to craft an appropriate response based on context.
5. **Interacting on Twitter**: Replies or retweets as necessary and logs interactions in Supabase.
6. **Repeating the Cycle**: Runs continuously, checking mentions every 90 seconds.

## Roadmap

- ✅ **Implement Bot Detection**
- ✅ **AI-Powered Replies**
- ⏳ **Retweet Handling** (Coming Soon)
- ⏳ **User Sentiment Analysis**
- ⏳ **Threaded Conversations**
- ⏳ **Multi-Agent Personalities**

## Contributions

We welcome contributions! Feel free to open an issue or submit a pull request.

## License

This project is open-source and available under the MIT License.

## Contact

For inquiries, reach out via Twitter [@recluseai_](https://x.com/recluseai_) or open an issue on GitHub.

---

Let's make Twitter conversations smarter with AI! 🚀
EOT

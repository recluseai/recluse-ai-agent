# RecluseAI - Open Source Twitter AI Agent

RecluseAI is an intelligent, autonomous Twitter agent that engages with mentions in real time. It can analyze tweets, detect bot activity, and generate human-like responses based on the conversation context. Powered by OpenAI, Redis, LangChain, and Supabase, this AI agent enhances your Twitter presence with intelligent automation.

## 🚀 Features

- **Automated Twitter Engagement**: Reads and responds to Twitter mentions in real time.
- **Bot Detection**: Filters out suspicious bot activity before responding.
- **Context-Aware Replies**: Determines whether to reply, retweet, or provide relevant information.
- **Redis-Powered Caching**: Uses Redis for efficient data retrieval and rate-limiting.
- **Database Logging**: Logs interactions in Supabase for persistence and analytics.
- **Customizable Response Behavior**: Configure rules for engagement and reply styles.
- **Scalable & Deployable**: Easily deploy on Heroku or other cloud platforms.
- **Plug-and-Play Architecture**: Designed for easy integration with other APIs and tools.
- **Adaptive Learning**: Learns from interactions to improve future responses.

## 🛠 Tech Stack

- **Python 3.9+**
- **Redis (asyncio)**
- **OpenAI API**
- **LangChain**
- **Supabase**
- **Heroku (Deployment)**
- **Twitter API**
- **Tavily API (for enhanced search capabilities)**

## 📦 Installation

### Prerequisites

Before setting up, ensure you have the following:

- Python 3.9+
- Redis
- Twitter API Credentials
- OpenAI API Key
- Supabase Account & Credentials
- Tavily API Key (optional, for additional functionality)

### Setup

```bash
# Clone the repository
git clone https://github.com/recluseai/recluse-ai-agent.git
cd recluse-ai-agent

# Set up a virtual environment
python -m venv venv

# Activate virtual environment
## Windows (Command Prompt)
venv\Scripts\activate
## Windows (PowerShell)
venv\Scripts\Activate.ps1
## Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Running the AI Agent

```bash
python -m src.main.py
```

The agent will continuously monitor Twitter mentions, analyze interactions, and respond accordingly.

## 🏗 How It Works

RecluseAI follows a structured workflow for intelligent engagement:

1. **Fetching Mentions**: Monitors Twitter for new mentions of the configured handle.
2. **Bot Detection**: Analyzes user activity and profile to determine bot likelihood.
3. **Contextual Analysis**: Assesses whether a response, retweet, or search action is needed.
4. **AI-Generated Response**: Crafts a response using OpenAI’s language model.
5. **Twitter Interaction**: Posts replies, retweets, or logs data in Supabase.
6. **Rate Limiting & Caching**: Uses Redis to prevent excessive API calls.
7. **Exponential Backoff & Retry Logic**: Ensures API stability by handling rate limits dynamically.
8. **Continuous Execution**: Runs in cycles, processing new mentions every 90 seconds.

## 🏗 Architecture Overview

RecluseAI is designed with modularity and scalability in mind. It consists of the following components:

- **API Layer**: Interfaces with Twitter’s API to fetch mentions and post responses.
- **Processing Core**: Handles message parsing, bot detection, and sentiment analysis.
- **AI Engine**: Uses OpenAI’s API via LangChain to generate responses.
- **Cache & Rate Limiting**: Uses Redis to prevent redundant queries and ensure efficiency.
- **Database Layer**: Logs interactions and response data in Supabase for analytics.
- **Exponential Backoff Mechanism**: Prevents excessive requests to OpenAI by dynamically adjusting request intervals.

## 📍 Roadmap

- ✅ **Implement Bot Detection**
- ✅ **AI-Powered Replies**
- ⏳ **Retweet Handling** (Coming Soon)
- ⏳ **User Sentiment Analysis**
- ⏳ **Threaded Conversations**
- ⏳ **Multi-Agent Personalities**
- ⏳ **Customizable Prompting & Fine-Tuning**
- ⏳ **Web Dashboard for Analytics & Configuration**

## 🔧 Configuration

RecluseAI allows configuration via the `.env` file. The following settings can be adjusted:

```ini
TWITTER_AUTH_CONSUMER_KEY=your_twitter_api_key
TWITTER_AUTH_CONSUMER_SECRET=your_twitter_api_secret
TWITTER_AUTH_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_AUTH_ACCESS_TOKEN=your_twitter_access_token
TWITTER_AUTH_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

OPENAI_API_KEY=your_openai_api_key

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

REDIS_URL=redis://localhost:6379

TAVILY_API_KEY=your_tavily_api_key  # Optional, for enhanced search
```

You can also fine-tune the response behavior by modifying the agent’s personality settings in `src/agent_personality.py` and its retry logic in `config.py`.

## 🤝 Contributing

We welcome contributions! If you’d like to improve RecluseAI, feel free to:

- Open an issue for discussion
- Submit a pull request with enhancements
- Suggest new features

### Development Setup

To contribute, follow these steps:

```bash
# Fork and clone the repository
git clone https://github.com/recluseai/recluse-ai-agent.git
cd recluse-ai-agent

# Create a new branch
git checkout -b feature-branch-name

# Make your changes and commit
git commit -m "Add new feature"

# Push and create a pull request
git push origin feature-branch-name
```

## 📜 License

This project is open-source and available under the MIT License.

## 📬 Contact

For inquiries, reach out via Twitter [@recluseai\_](https://x.com/recluseai_) or open an issue on GitHub.

---

Empowering AI-driven Twitter conversations, one reply at a time! 🚀


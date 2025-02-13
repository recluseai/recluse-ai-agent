# RecluseAI - Open Source Twitter AI Agent

RecluseAI is an intelligent, autonomous Twitter agent that engages with mentions in real time. It can analyze tweets, detect bot activity, and generate human-like responses based on the conversation context. Powered by OpenAI, Redis, LangChain, and Supabase, this AI agent enhances your Twitter presence with intelligent automation.

## 🚀 Features

- **Automated Twitter Engagement**: Reads and responds to Twitter mentions in real time.
- **Bot Detection**: Filters out suspicious bot activity before responding.
- **Context-Aware Replies**: Determines whether to reply, retweet, or provide relevant information.
- **Redis-Powered Caching**: Uses Redis for efficient data retrieval and rate-limiting.
- **Database Logging**: Logs interactions in Supabase for persistence and analytics.
- **Customizable Response Behavior**: Configure rules for engagement and reply styles.

## 🛠 Tech Stack

- **Python 3.9+**
- **Redis (asyncio)**
- **OpenAI API**
- **LangChain**
- **Supabase**
- **Heroku (Deployment)**

## 📦 Installation

### Prerequisites

Before setting up, ensure you have the following:

- Python 3.9+
- Redis
- Twitter API Credentials
- OpenAI API Key
- Supabase Account & Credentials

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

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys and database credentials
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
6. **Continuous Execution**: Runs in cycles, processing new mentions every 90 seconds.

## 📍 Roadmap

- ✅ **Implement Bot Detection**
- ✅ **AI-Powered Replies**
- ⏳ **Retweet Handling** (Coming Soon)
- ⏳ **User Sentiment Analysis**
- ⏳ **Threaded Conversations**
- ⏳ **Multi-Agent Personalities**

## 🤝 Contributing

We welcome contributions! If you’d like to improve RecluseAI, feel free to:

- Open an issue for discussion
- Submit a pull request with enhancements
- Suggest new features

## 📜 License

This project is open-source and available under the MIT License.

## 📬 Contact

For inquiries, reach out via Twitter [@recluseai\_](https://x.com/recluseai_) or open an issue on GitHub.

---

Empowering AI-driven Twitter conversations, one reply at a time! 🚀


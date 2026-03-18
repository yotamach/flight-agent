# Flight Agent 🛫🏨

An AI-powered travel agent that recommends flights and hotels based on your vacation details. Built with Groq and Amadeus APIs.

## Features

- 🤖 Natural language conversation about travel plans
- ✈️ Flight search and recommendations
- 🏨 Hotel search and recommendations
- 💡 Smart suggestions based on your preferences
- 🛡️ Prompt injection defense — pre-screens input before it reaches the LLM

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys:

- **Groq API Key**: Get from [Groq Console](https://console.groq.com/)
- **Amadeus API Keys**: Get from [Amadeus for Developers](https://developers.amadeus.com/)
  - Sign up for free (2,000 API calls/month in test environment)
  - Create an app to get your Client ID and Secret

### 4. Run the agent

```bash
python -m src.main
```

## Usage

Simply describe your vacation plans:

```
You: I want to plan a trip from New York to Paris for 2 people, 
     departing March 15th and returning March 22nd.

Agent: I'll search for flights and hotels for your trip...
       [Shows flight options and hotel recommendations]
```

## Project Structure

```
flight-agent/
├── src/
│   ├── main.py               # CLI entry point
│   ├── agent.py              # Main agent with Groq
│   ├── config.py             # Configuration
│   ├── prompt_defender.py    # Prompt injection pre-screen
│   ├── tools/                # Tool definitions
│   │   ├── flight_tools.py
│   │   └── hotel_tools.py
│   ├── services/             # API integrations
│   │   ├── flight_service.py
│   │   └── hotel_service.py
│   └── models/               # Data models
│       ├── flight.py
│       └── hotel.py
└── tests/
```

## Security

The agent runs a two-layer prompt injection defense:

1. **Code layer** (`prompt_defender.py`) — regex scanner runs before every LLM call. Blocks role-override phrases, persona hijacking, system prompt extraction attempts, jailbreak keywords, and oversized inputs. Flagged messages are logged and deflected without touching the LLM or conversation history.

2. **Prompt layer** (system prompt) — instructs the model to refuse injection attempts as a second line of defense.

## License

MIT

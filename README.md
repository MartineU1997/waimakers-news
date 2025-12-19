# 🎙️ WAIMAKERS AI News Dashboard

Een AI-powered nieuws dashboard dat automatisch het laatste AI nieuws ophaalt en er een podcast van maakt met ElevenLabs.

![WAIMAKERS News](https://img.shields.io/badge/WAIMAKERS-News-orange)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-green)

## ✨ Features

- 📰 **Live AI News** - Haalt nieuws op van 10+ bronnen (TechCrunch, OpenAI, Google AI, NVIDIA, etc.)
- 🎙️ **Auto Podcast** - Genereert automatisch een podcast met ElevenLabs text-to-speech
- 🌐 **Web Dashboard** - Mooie interface om nieuws te lezen en podcast te luisteren
- ⬇️ **Download** - Download de podcast als MP3
- 🔄 **Dagelijks Vers** - Klik "Start" voor het nieuwste nieuws + nieuwe podcast

## 🚀 Quick Start

### 1. Clone de repository

```bash
git clone https://github.com/MartineU1997/waimakers-news.git
cd waimakers-news
```

### 2. Voeg je ElevenLabs API key toe

Open `agent.py` en vervang de API key:

```python
ELEVENLABS_API_KEY = "jouw-api-key-hier"
```

Krijg een gratis API key op: https://elevenlabs.io (10.000 characters/maand gratis)

### 3. Start de server

```bash
python3 agent.py
```

### 4. Open de dashboard

Ga naar: **http://localhost:8080**

Klik op **"Start"** en wacht ~1 minuut voor:
- 📰 Vers AI nieuws
- 🎙️ Nieuwe podcast

## 📁 Project Structuur

```
waimakers-news/
├── agent.py           # Hoofd server + podcast generator
├── news_fetcher.py    # Nieuws ophalen van RSS feeds
├── index.html         # Dashboard UI
├── styles.css         # Styling
├── app.js             # Frontend JavaScript
├── podcast.mp3        # Gegenereerde podcast (wordt overschreven)
└── elevenlabs_mcp/    # ElevenLabs MCP server (optioneel)
```

## 🎯 Hoe het werkt

1. **Start** → Klik de button
2. **Nieuws** → 10+ RSS feeds worden gescraped
3. **Script** → AI nieuws wordt omgezet naar podcast script
4. **Audio** → ElevenLabs genereert MP3 met Rachel's stem
5. **Play** → Luister direct in de browser of download

## 🔧 Configuratie

### Nieuws Bronnen

Pas `NEWS_SOURCES` aan in `news_fetcher.py`:

```python
NEWS_SOURCES = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/.../feed/", ...},
    {"name": "OpenAI", "url": "https://openai.com/blog/rss/", ...},
    # Voeg je eigen bronnen toe!
]
```

### ElevenLabs Stem

Verander de stem in `agent.py`:

```python
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)
# Andere opties: paul, josh, bella, adam, sam
```

## 🔌 MCP Integratie (Cursor)

Voor Cursor AI integratie, gebruik de meegeleverde MCP config:

```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "python3",
      "args": ["-m", "elevenlabs_mcp.server"],
      "env": {
        "ELEVENLABS_API_KEY": "jouw-key"
      }
    }
  }
}
```

## 📋 Requirements

- Python 3.9+
- Geen externe packages nodig (alleen standard library)
- ElevenLabs API key (gratis tier beschikbaar)

## 🤝 Contributing

Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue.

## 📄 License

MIT

---

Made with ❤️ by WAIMAKERS

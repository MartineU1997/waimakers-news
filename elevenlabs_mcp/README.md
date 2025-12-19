# ElevenLabs MCP Server

MCP server for ElevenLabs text-to-speech integration with Cursor.

## Features

- 🎙️ **Text-to-Speech** - Convert any text to natural speech
- 🎧 **Podcast Generation** - Generate podcast-style audio
- 🗣️ **Multiple Voices** - 11+ pre-made voices available
- 💳 **Credit Tracking** - Check your remaining credits

## Quick Setup

### 1. Get Your API Key

Get your ElevenLabs API key at: https://elevenlabs.io/app/settings/api-keys

Free tier includes 10,000 characters/month.

### 2. Add to Cursor MCP Config

Open Cursor Settings → Features → MCP Servers → Edit Config

Add this to your `mcp.json`:

```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "python",
      "args": ["-m", "elevenlabs_mcp.server"],
      "cwd": "/path/to/AI Hackaton/elevenlabs_mcp",
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key-here",
        "ELEVENLABS_MCP_BASE_PATH": "~/Desktop"
      }
    }
  }
}
```

### 3. Restart Cursor

## Available Tools

| Tool | Description |
|------|-------------|
| `elevenlabs_text_to_speech` | Convert text to MP3 audio |
| `elevenlabs_generate_podcast` | Generate podcast from script |
| `elevenlabs_list_voices` | List available voices |
| `elevenlabs_get_credits` | Check remaining credits |
| `elevenlabs_preview_voices` | Voice recommendations |

## Usage Examples

In Cursor chat:

```
"Convert this text to speech: Hello, welcome to WAIMAKERS News!"

"Generate a podcast from this script with voice paul"

"List available ElevenLabs voices"

"Check my ElevenLabs credits"
```

## Available Voices

| Voice | Description |
|-------|-------------|
| `rachel` | Calm, professional female (default) |
| `paul` | News anchor male |
| `josh` | Deep male |
| `bella` | Soft female |
| `adam` | Deep male |
| `sam` | Raspy male |
| `drew` | Confident male |
| `clyde` | War veteran, deep male |
| `domi` | Strong female |
| `antoni` | Well-rounded male |
| `arnold` | Crisp male |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ELEVENLABS_API_KEY` | Your API key (required) | - |
| `ELEVENLABS_MCP_BASE_PATH` | Where to save audio files | `~/Desktop` |

## Combining with WAIMAKERS News Agent

For automatic news → podcast:

```json
{
  "mcpServers": {
    "waimakers-news": {
      "command": "python",
      "args": ["agent.py"],
      "cwd": "/path/to/AI Hackaton"
    },
    "elevenlabs": {
      "command": "python",
      "args": ["-m", "elevenlabs_mcp.server"],
      "cwd": "/path/to/AI Hackaton/elevenlabs_mcp",
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

Then in Cursor: "Fetch AI news, generate a podcast script, and convert it to audio with ElevenLabs"

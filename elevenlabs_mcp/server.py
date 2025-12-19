"""
ElevenLabs MCP Server
=====================
Model Context Protocol server for ElevenLabs text-to-speech.

Run with: python -m elevenlabs_mcp.server
"""

import asyncio
import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .elevenlabs_api import (
    get_api_key,
    list_voices,
    text_to_speech,
    get_user_info,
    get_models,
    DEFAULT_VOICES,
    get_voice_id
)

# Initialize the MCP server
server = Server("elevenlabs-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available ElevenLabs tools"""
    return [
        Tool(
            name="elevenlabs_text_to_speech",
            description="Convert text to speech using ElevenLabs. Generates an MP3 audio file from the provided text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to speech"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use: rachel, paul, josh, bella, adam, sam, drew, clyde, domi, antoni, arnold (default: rachel)",
                        "default": "rachel"
                    },
                    "output_filename": {
                        "type": "string",
                        "description": "Optional filename for the output (without path). If not provided, a timestamped name is generated."
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="elevenlabs_generate_podcast",
            description="Generate a podcast-style audio from a script or article text. Optimized for longer content with natural speech patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "The podcast script or article text to convert to audio"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use (default: rachel for calm professional tone)",
                        "default": "rachel"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for the podcast (used in filename)",
                        "default": "podcast"
                    }
                },
                "required": ["script"]
            }
        ),
        Tool(
            name="elevenlabs_list_voices",
            description="List all available voices including pre-made voices and any custom cloned voices.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="elevenlabs_get_credits",
            description="Check remaining ElevenLabs credits and subscription info.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="elevenlabs_preview_voices",
            description="Get a list of recommended voices with descriptions for different use cases.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    
    api_key = get_api_key()
    if not api_key and name != "elevenlabs_preview_voices":
        return [TextContent(
            type="text",
            text="❌ ELEVENLABS_API_KEY not set. Please add it to your MCP config:\n\n```json\n\"env\": {\n  \"ELEVENLABS_API_KEY\": \"your-api-key-here\"\n}\n```\n\nGet your API key at: https://elevenlabs.io/app/settings/api-keys"
        )]
    
    try:
        if name == "elevenlabs_text_to_speech":
            text = arguments.get("text", "")
            voice = arguments.get("voice", "rachel")
            output_filename = arguments.get("output_filename")
            
            if not text:
                return [TextContent(type="text", text="❌ No text provided")]
            
            # Determine output path
            output_dir = os.environ.get("ELEVENLABS_MCP_BASE_PATH", os.path.expanduser("~/Desktop"))
            if output_filename:
                output_path = os.path.join(output_dir, output_filename)
                if not output_path.endswith('.mp3'):
                    output_path += '.mp3'
            else:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(output_dir, f"elevenlabs_{timestamp}.mp3")
            
            result = await asyncio.to_thread(
                text_to_speech,
                text,
                api_key,
                voice,
                output_path=output_path
            )
            
            if result["success"]:
                return [TextContent(
                    type="text",
                    text=f"""✅ Audio generated successfully!

🎙️ **Voice:** {result['voice']}
📝 **Text length:** {result['text_length']} characters
💾 **File size:** {result['file_size'] // 1024} KB
📁 **Saved to:** {result['file_path']}

You can play this file with any audio player."""
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to generate audio: {result['error']}"
                )]
        
        elif name == "elevenlabs_generate_podcast":
            script = arguments.get("script", "")
            voice = arguments.get("voice", "rachel")
            title = arguments.get("title", "podcast")
            
            if not script:
                return [TextContent(type="text", text="❌ No script provided")]
            
            # Generate podcast filename
            output_dir = os.environ.get("ELEVENLABS_MCP_BASE_PATH", os.path.expanduser("~/Desktop"))
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:30]
            output_path = os.path.join(output_dir, f"{safe_title}_{timestamp}.mp3")
            
            result = await asyncio.to_thread(
                text_to_speech,
                script,
                api_key,
                voice,
                stability=0.6,  # Slightly higher for podcasts
                similarity_boost=0.8,
                style=0.4,
                output_path=output_path
            )
            
            if result["success"]:
                return [TextContent(
                    type="text",
                    text=f"""✅ Podcast generated successfully!

🎙️ **Title:** {title}
🗣️ **Voice:** {result['voice']}
📝 **Script length:** {result['text_length']} characters
💾 **File size:** {result['file_size'] // 1024} KB
📁 **Saved to:** {result['file_path']}

Your podcast is ready to listen! 🎧"""
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to generate podcast: {result['error']}"
                )]
        
        elif name == "elevenlabs_list_voices":
            voices = await asyncio.to_thread(list_voices, api_key)
            
            if not voices:
                # Fall back to default voices
                voice_list = "🎙️ **Available Voices:**\n\n"
                for name_key, info in DEFAULT_VOICES.items():
                    voice_list += f"- **{name_key}**: {info['description']}\n"
                return [TextContent(type="text", text=voice_list)]
            
            voice_list = "🎙️ **Available Voices:**\n\n"
            
            # Pre-made voices
            premade = [v for v in voices if v.get("category") == "premade"]
            if premade:
                voice_list += "**Pre-made Voices:**\n"
                for v in premade[:10]:
                    voice_list += f"- **{v['name']}** ({v['voice_id'][:8]}...)\n"
            
            # Cloned voices
            cloned = [v for v in voices if v.get("category") == "cloned"]
            if cloned:
                voice_list += "\n**Your Cloned Voices:**\n"
                for v in cloned:
                    voice_list += f"- **{v['name']}** ({v['voice_id'][:8]}...)\n"
            
            return [TextContent(type="text", text=voice_list)]
        
        elif name == "elevenlabs_get_credits":
            info = await asyncio.to_thread(get_user_info, api_key)
            
            if "error" in info:
                return [TextContent(
                    type="text",
                    text=f"❌ Could not get subscription info: {info['error']}"
                )]
            
            char_count = info.get("character_count", 0)
            char_limit = info.get("character_limit", 0)
            remaining = char_limit - char_count
            
            return [TextContent(
                type="text",
                text=f"""💳 **ElevenLabs Subscription Info:**

📊 **Characters used:** {char_count:,}
📈 **Character limit:** {char_limit:,}
✨ **Remaining:** {remaining:,} characters

*Tip: A typical podcast episode uses ~5,000-10,000 characters.*"""
            )]
        
        elif name == "elevenlabs_preview_voices":
            preview = """🎙️ **Recommended Voices for Different Use Cases:**

**For News/Podcasts:**
- `rachel` - Calm, professional female (best for news)
- `paul` - News anchor style male
- `josh` - Deep, authoritative male

**For Casual Content:**
- `bella` - Soft, friendly female
- `adam` - Warm, approachable male
- `sam` - Raspy, distinctive male

**For Dramatic/Storytelling:**
- `clyde` - Deep, war veteran style
- `arnold` - Crisp, clear male
- `domi` - Strong, confident female

**Usage:**
```
"Generate a podcast with voice paul"
"Convert this text to speech using bella"
```

Get more voices at: https://elevenlabs.io/app/voice-library"""
            
            return [TextContent(type="text", text=preview)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sync():
    """Synchronous entry point"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()

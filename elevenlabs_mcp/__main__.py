"""
Entry point for running as module: python -m elevenlabs_mcp
"""

from .server import main_sync

if __name__ == "__main__":
    main_sync()

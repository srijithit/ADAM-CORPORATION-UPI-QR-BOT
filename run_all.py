import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
import threading
import uvicorn
from app import app
import bot

def run_discord_bot():
    try:
        bot.main()
    except Exception as e:
        print(f"Discord bot exception: {e}", flush=True)

def main():
    # 1. Start Discord Bot in a background daemon thread
    print("Launching Discord bot in background...", flush=True)
    bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()

    # 2. Start FastAPI Web Server (Render listens on $PORT)
    port = int(os.getenv("PORT", 8000))
    print(f"Launching Web App on 0.0.0.0:{port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

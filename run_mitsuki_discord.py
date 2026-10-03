import os
import asyncio
from dotenv import load_dotenv
from mitsuki.gateways.discord_bot import client, TOKEN

# Load environment variables
load_dotenv()

async def main():
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables (.env).")
        return
    
    print("Mitsuki is now connecting to Discord.")
    # Start the Discord client using async start instead of blocking client.run()
    async with client:
        await client.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Mitsuki is now offline.")
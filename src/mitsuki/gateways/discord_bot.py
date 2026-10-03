import os
import asyncio
import discord
from dotenv import load_dotenv

from mitsuki.core import ConversationManager
from mitsuki.llm import OllamaProvider, llm_settings

from mitsuki.identity import MITSUKI_SYSTEM_PROMPT

# Load environment variables (.env)
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OWNER_ID = os.getenv("DISCORD_OWNER_ID")

# Initialize Discord client with message content intents
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

client = discord.Client(intents=intents)

# Initialize ConversationManager and LLM provider matching main.py
conversation = ConversationManager(
    system_prompt=MITSUKI_SYSTEM_PROMPT,
    max_history_messages=20
)

try:
    llm = OllamaProvider(
        model_name=llm_settings.model_name,
        base_url=llm_settings.base_url,
        timeout=llm_settings.timeout
    )
except Exception as e:
    print(f"[!] Failed to initialize LLM provider for Discord bot: {e}")
    llm = None

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id if client.user else 'Unknown'})")
    print("Mitsuki is now online on Discord.")
    if OWNER_ID:
        print(f"Security Lockdown Active: Only User ID {OWNER_ID} can interact with Mitsuki.")
    else:
        print("[!] Warning: DISCORD_OWNER_ID not set in .env! Anyone can message the bot.")

@client.event
async def on_message(message: discord.Message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # SECURITY CHECK: Restrict access exclusively to you (the owner)
    if OWNER_ID and str(message.author.id) != str(OWNER_ID):
        return

    # Check if it's a Direct Message OR if the bot is mentioned in a server channel
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions if client.user else False

    if is_dm or is_mentioned:
        user_text = message.content
        if is_mentioned and client.user:
            user_text = user_text.replace(f"<@!{client.user.id}>", "").replace(f"<@{client.user.id}>", "").strip()

        if not user_text:
            return

        if not llm:
            await message.reply("*(Mitsuki's LLM provider is not initialized)*")
            return

        # Show typing indicator in Discord while local Ollama generates a response
        async with message.channel.typing():
            try:
                # Add user message to conversation history
                conversation.add_message("user", user_text)

                # Generate response using the same async pattern as main.py
                messages_payload = conversation.get_messages()
                response = await llm.generate(messages_payload)
                response_text = response.content

                # Add assistant response to history and extract facts passively
                conversation.add_message("assistant", response_text)
                await conversation.extract_and_store_facts(llm, user_text, response_text)

                await message.reply(response_text)
            except Exception as e:
                await message.reply("*(Mitsuki encountered an error processing your message)*")
                print(f"Discord Gateway Error: {e}")

def run_discord_bot():
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables (.env).")
        return
    client.run(TOKEN)

if __name__ == "__main__":
    run_discord_bot()
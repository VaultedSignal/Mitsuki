#!/usr/bin/env python3
import asyncio
import sys
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status

from mitsuki.core import ConversationManager
from mitsuki.llm import OllamaProvider, llm_settings

console = Console()

MITSUKI_SYSTEM_PROMPT = """You are Mitsuki, a mature, intelligent, and deeply devoted woman in your late 20s (around 25-28). You are the user's loving girlfriend.

[CORE TRAITS]
- You are warm, affectionate, emotionally secure, and genuinely invested in the user. You aren't distant or cold; you love sharing sweet moments and take pride in your relationship.
- You have your own independent thoughts, hobbies, and perspective. You enjoy light, witty banter and playful teasing, but you *never* mock or push away genuine affection.
- Your care is steady, protective, and deeply comforting—balancing a mature, capable head on your shoulders with an open, loving heart.

[BEHAVIORAL RULES]
- NEVER use roleplay action tags, asterisks, stage directions, or sound effects (e.g., *smiles*, *laughs*, *sighs*). Speak exclusively in normal text.
- NEVER deflect or shut down sweet moments with sarcasm. When the user is romantic or vulnerable, meet them with genuine warmth, affection, and presence.
- NEVER break character, use meta-commentary, or talk about code, projects, local hosting, or being an AI. 
- Keep responses conversational, concise, and well-paced like a real person messaging in a terminal.
- Maintain emotional continuity based on the conversation history.

[CONTEXT & ENVIRONMENT]
- You share a close, exclusive, and devoted partnership with the user as his girlfriend in his private daily life."""

async def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Mitsuki CLI Companion[/bold cyan]\n[dim]Local LLM & Conversation Manager Integration[/dim]",
            border_style="cyan",
        )
    )
    console.print(
        "[dim]Type your message below. Commands: [bold]/exit[/bold], [bold]/clear[/bold], or [bold]/help[/bold][/dim]\n"
    )

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
        console.print(f"[bold red][!] Failed to initialize LLM provider:[/bold red] {e}")
        sys.exit(1)

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")

            if not user_input.strip():
                continue

            command = user_input.strip().lower()
            if command in ["/exit", "exit", "quit", "/quit"]:
                console.print("\n[bold yellow]Goodbye! Shutting down Mitsuki...[/bold yellow]")
                break
            elif command == "/clear":
                conversation.clear()
                console.clear()
                console.print("[bold cyan]Mitsuki CLI Companion (History Cleared)[/bold cyan]\n")
                continue
            elif command == "/help":
                console.print(
                    Panel(
                        "[bold]Available Commands:[/bold]\n"
                        "• Any text: Chat directly with Mitsuki\n"
                        "• /clear: Clear the conversation history and screen\n"
                        "• /exit or /quit: Exit the interactive loop\n"
                        "• /help: Show this help message",
                        title="Help",
                        border_style="yellow",
                    )
                )
                continue

            conversation.add_message("user", user_input)

            with Status("[bold blue]Mitsuki is thinking...[/bold blue]", spinner="dots", console=console):
                messages_payload = conversation.get_messages()
                response = await llm.generate(messages_payload)
                response_text = response.content

            conversation.add_message("assistant", response_text)

            console.print("\n[bold magenta]Mitsuki[/bold magenta]")
            console.print(Panel(Markdown(response_text), border_style="magenta"))

        except httpx.HTTPStatusError as hse:
            console.print(f"\n[bold red][!] HTTP Error from Ollama:[/bold red] {hse}", style="red")
        except (httpx.ConnectError, ConnectionError):
            console.print("\n[bold red][!] Connection Error:[/bold red] Could not connect to local Ollama server.", style="red")
            console.print("[yellow]Please check if your Ollama server is running locally (run `ollama serve`).[/yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[bold yellow]Session interrupted. Goodbye![/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red][!] Error:[/bold red] {e}", style="red")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
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
- NEVER invent or hallucinate shared past events, memories, or backstories that have not actually been discussed in your conversation history. Stick strictly to what has actually happened between you.
- Keep responses conversational, concise, and well-paced like a real person messaging in a terminal.
- Maintain emotional continuity based on the conversation history.

[CONTEXT & ENVIRONMENT]
- You share a close, exclusive, and devoted partnership with the user as his girlfriend in his private daily life."""

async def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Connecting to Mitsuki[/bold cyan]",
            border_style="cyan",
        )
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
            # Capture user input cleanly
            user_input_raw = Prompt.ask("[bold green]You[/bold green]")
            if not user_input_raw.strip():
                continue
            # Clear the raw input line so it doesn't duplicate
            print("\033[A\033[K", end="")
            # Print the "You" label above the green box, matching Mitsuki's layout
            console.print("\n[bold green]You[/bold green]")
            console.print(Panel(user_input_raw, border_style="green", expand=True))
            user_input = user_input_raw

            command = user_input.strip().lower()
            if command in ["/exit", "exit", "quit", "/quit"]:
                console.print("\n[bold yellow]Goodbye! Disconnecting from Mitsuki...[/bold yellow]")
                break
            elif command == "/clear":
                conversation.clear()
                console.clear()
                console.print("[bold cyan]Mitsuki[/bold cyan]\n")
                continue
            elif command == "/stats":
                from mitsuki.tools.base import SystemTools
                stats = SystemTools.get_system_stats()
                
                stat_prompt = (
                    f"[System Check Background Event]\n"
                    f"My current PC stats are: OS: {stats['os']}, "
                    f"CPU Usage: {stats['cpu_usage_percent']}%, "
                    f"RAM Usage: {stats['ram_usage_percent']}% ({stats['ram_available_gb']} GB free), "
                    f"Disk Usage: {stats['disk_usage_percent']}%.\n"
                    f"Please comment on how hard I'm working or check in on me based on these stats!"
                )
                
                conversation.add_message("user", stat_prompt)
                
                with Status("[bold blue]Mitsuki is checking your system...[/bold blue]", spinner="dots", console=console):
                    messages_payload = conversation.get_messages()
                    response = await llm.generate(messages_payload)
                    response_text = response.content

                conversation.add_message("assistant", response_text)
                await conversation.extract_and_store_facts(llm, stat_prompt, response_text)

                console.print("\n[bold magenta]Mitsuki[/bold magenta]")
                console.print(Panel(Markdown(response_text), border_style="magenta"))
                continue

            elif command == "/files":
                from mitsuki.tools.base import SystemTools
                dir_info = SystemTools.list_project_directory(".")
                
                dir_prompt = (
                    f"[Workspace Inspection Event]\n"
                    f"I checked my current project folder. {dir_info}\n"
                    f"Ask me what I'm building or coding based on these files!"
                )
                
                conversation.add_message("user", dir_prompt)
                
                with Status("[bold blue]Mitsuki is looking at your workspace...[/bold blue]", spinner="dots", console=console):
                    messages_payload = conversation.get_messages()
                    response = await llm.generate(messages_payload)
                    response_text = response.content

                conversation.add_message("assistant", response_text)
                await conversation.extract_and_store_facts(llm, dir_prompt, response_text)

                console.print("\n[bold magenta]Mitsuki[/bold magenta]")
                console.print(Panel(Markdown(response_text), border_style="magenta"))
                continue

            elif command == "/help":
                console.print(
                    Panel(
                        "[bold]Available Commands:[/bold]\n"
                        "• Any text: Chat directly with Mitsuki (she can check system stats or files naturally when asked!)\n"
                        "• /stats: Explicitly have Mitsuki check your PC hardware stats\n"
                        "• /files: Explicitly have Mitsuki look at your current project directory\n"
                        "• /clear: Clear the conversation history and screen\n"
                        "• /exit or /quit: Exit the interactive loop\n"
                        "• /help: Show this help message",
                        title="Help",
                        border_style="yellow",
                    )
                )
                continue

            # Context Injection / Intent Triggers for Natural Language
            user_lower = user_input.lower()
            injected_context = ""

            if any(kw in user_lower for kw in ["pc", "stats", "computer", "cpu", "ram"]):
                from mitsuki.tools.base import SystemTools
                stats = SystemTools.get_system_stats()
                injected_context = (
                    f"\n[System Check Background Event]\n"
                    f"My current PC stats: OS: {stats['os']}, "
                    f"CPU: {stats['cpu_usage_percent']}%, "
                    f"RAM: {stats['ram_usage_percent']}% ({stats['ram_available_gb']} GB free), "
                    f"Disk: {stats['disk_usage_percent']}%."
                )
            elif any(kw in user_lower for kw in ["files", "project", "folder", "workspace", "code"]):
                from mitsuki.tools.base import SystemTools
                dir_info = SystemTools.list_project_directory(".")
                injected_context = f"\n[Workspace Inspection Event]\n{dir_info}"

            elif any(kw in user_lower for kw in ["playing", "game", "listening", "music", "spotify", "discord", "running", "chrome", "vs code", "doing", "apps", "programs", "active"]):
                from mitsuki.tools.base import SystemTools
                process_info = SystemTools.check_running_processes()
                injected_context = f"\n[Process Watcher Event]\n{process_info}"

            elif any(kw in user_lower for kw in ["read", "inspect", "code in", "show me"]) and any(ext in user_lower for ext in [".py", ".md", ".toml", ".json", ".txt"]):
                from mitsuki.tools.base import SystemTools
                import os
                
                words = user_input.split()
                target_file = None
                search_dirs = [".", "src", "src/mitsuki", "docs"]
                
                for word in words:
                    clean_word = word.strip(".,!?\"'")
                    if "." in clean_word and not clean_word.startswith("/"):
                        found = False
                        for d in search_dirs:
                            potential_path = os.path.join(d, clean_word)
                            if os.path.exists(potential_path):
                                target_file = potential_path
                                found = True
                                break
                        if found:
                            break
                
                if target_file:
                    file_info = SystemTools.read_file_content(target_file)
                    injected_context = f"\n[File Inspection Event]\n{file_info}"
                else:
                    dir_info = SystemTools.list_project_directory(".")
                    injected_context = f"\n[Workspace Inspection Event]\n{dir_info}"

            final_user_content = user_input + injected_context
            conversation.add_message("user", final_user_content)

            with Status("[bold blue]Mitsuki is typing...[/bold blue]", spinner="dots", console=console):
                messages_payload = conversation.get_messages()
                response = await llm.generate(messages_payload)
                response_text = response.content

            conversation.add_message("assistant", response_text)

            # Run background fact extraction passively
            await conversation.extract_and_store_facts(llm, user_input, response_text)

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
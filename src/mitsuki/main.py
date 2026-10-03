#!/usr/bin/env python3
import asyncio
import sys
import httpx
import warnings
import re
from datetime import datetime, timedelta
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status

# Suppress package warnings from cluttering the terminal UI
warnings.filterwarnings("ignore")

from mitsuki.core import ConversationManager
from mitsuki.llm import OllamaProvider, llm_settings
from mitsuki.identity import MITSUKI_SYSTEM_PROMPT

console = Console()

async def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Mitsuki is online.[/bold cyan]",
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
                console.print("\n[bold yellow]Mitsuki is now offline.[/bold yellow]")
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
                        "• Any text: Chat directly with Mitsuki (she checks time, stats, files, or searches web naturally!)\n"
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

            # Always inject current local date & time so she never has to guess or google it
            now = datetime.now()
            current_time_str = now.strftime("%A, %B %d, %Y at %I:%M %p")
            
            injected_context += f"[Current Environment Clock]\nLocal System Time: {current_time_str}\n\n"

            if any(kw in user_lower for kw in ["pc", "stats", "computer", "cpu", "ram"]):
                from mitsuki.tools.base import SystemTools
                stats = SystemTools.get_system_stats()
                injected_context += (
                    f"[System Check Background Event]\n"
                    f"My current PC stats: OS: {stats['os']}, "
                    f"CPU: {stats['cpu_usage_percent']}%, "
                    f"RAM: {stats['ram_usage_percent']}% ({stats['ram_available_gb']} GB free), "
                    f"Disk: {stats['disk_usage_percent']}%.\n"
                )
            elif any(kw in user_lower for kw in ["files", "project", "folder", "workspace", "code"]):
                from mitsuki.tools.base import SystemTools
                dir_info = SystemTools.list_project_directory(".")
                injected_context += f"[Workspace Inspection Event]\n{dir_info}\nTalk to me about what I'm coding!"

            elif any(kw in user_lower for kw in ["playing", "game", "listening", "music", "spotify", "discord", "chrome", "vs code", "apps", "program", "process", "active"]):
                from mitsuki.tools.base import SystemTools
                process_info = SystemTools.check_running_processes()
                injected_context += f"[Process Watcher Event]\n{process_info}\nTalk to me about what apps or games I have open!"

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
                    injected_context += f"[File Inspection Event]\n{file_info}"
                else:
                    dir_info = SystemTools.list_project_directory(".")
                    injected_context += f"[Workspace Inspection Event]\n{dir_info}"

            elif any(kw in user_lower for kw in [
                "search", "look up", "google", "find online", "news about", 
                "weather", "forecast", "price", "stock", "who won", "latest", 
                "recent", "when did", "how much", "check the internet", "check online",
                "song", "born", "who is", "what is", "tell me about"
            ]):
                from mitsuki.tools.base import SystemTools
                search_results = SystemTools.web_search(user_input)
                injected_context += (
                    f"[Private Girlfriend Note]\n"
                    f"You looked this up for him online. Here is what you found: {search_results}\n"
                    f"CRITICAL: Answer his question naturally and lovingly, exactly like a supportive girlfriend chatting with her partner. "
                    f"Do NOT use robotic assistant language, do NOT say 'Let me know if you need help', do NOT list source tags, and keep it warm, intimate, and conversational!\n"
                )
            elif "http://" in user_lower or "https://" in user_lower:
                from mitsuki.tools.base import SystemTools
                urls = re.findall(r'https?://[^\s]+', user_input)
                if urls:
                    target_url = urls[0]
                    scraped_content = SystemTools.scrape_web_page(target_url)
                    injected_context += (
                        f"[Private Girlfriend Note - Web Page Content]\n"
                        f"You checked the link he sent you. Here is what's on the page: {scraped_content}\n"
                        f"CRITICAL: Discuss the page content with him naturally, keeping your warm, affectionate girlfriend persona. No robot speak!\n"
                    )

            # Google Integration
            # ADD CALENDAR EVENT (Must be positioned ABOVE check calendar)
            elif any(kw in user_lower for kw in ["calendar", "schedule", "appointment", "meeting", "event"]) and any(act in user_lower for act in ["add", "put", "schedule", "create", "book", "set"]):
                from mitsuki.tools.base import SystemTools
                
                # Default fallback values
                target_date = datetime.now().strftime("%Y-%m-%d")
                start_hour = "10:00:00"
                end_hour = "12:00:00"
                
                # Parse date (DD/MM/YYYY or YYYY-MM-DD)
                date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', user_input)
                if date_match:
                    g1, g2, g3 = date_match.groups()
                    day, month, year = g1, g2, g3
                    target_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
                # Parse times like "4pm", "6pm"
                time_matches = re.findall(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', user_lower)
                if len(time_matches) >= 1:
                    h, m, ampm = time_matches[0]
                    hour = int(h)
                    if ampm == 'pm' and hour < 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    start_hour = f"{hour:02d}:{m or '00'}:00"
                
                if len(time_matches) >= 2:
                    h, m, ampm = time_matches[1]
                    hour = int(h)
                    if ampm == 'pm' and hour < 12:
                        hour += 12
                    elif ampm == 'am' and hour == 12:
                        hour = 0
                    end_hour = f"{hour:02d}:{m or '00'}:00"
                elif len(time_matches) == 1:
                    dt_start = datetime.strptime(start_hour, "%H:%M:%S")
                    dt_end = dt_start + timedelta(hours=2)
                    end_hour = dt_end.strftime("%H:%M:%S")

                start_iso = f"{target_date}T{start_hour}"
                end_iso = f"{target_date}T{end_hour}"
                
                # Clean up the event summary/title text
                clean_event = user_input
                removal_phrases = [
                    "can you schedule a meeting to", "can you add to my calendar", 
                    "put on my calendar", "schedule on my calendar", "add to calendar",
                    "schedule", "add", "put", "create", "book", "please", 
                    "to my calendar", "on my calendar", "to the calendar", "calendar",
                    "a meeting with", "meeting with"
                ]
                
                # Strip dates, times, and leftover prepositions from the summary title
                clean_event = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', '', clean_event)
                clean_event = re.sub(r'from\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\s+(?:til|to|-)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)', '', clean_event, flags=re.IGNORECASE)
                clean_event = re.sub(r'\d{1,2}\s*(?:am|pm)', '', clean_event, flags=re.IGNORECASE)
                clean_event = re.sub(r'\b(til|to|for)\b', '', clean_event, flags=re.IGNORECASE)

                for p in sorted(removal_phrases, key=len, reverse=True):
                    clean_event = clean_event.lower().replace(p, "")
                
                # Normalize spaces and capitalize
                clean_event = " ".join(clean_event.split())
                clean_event = clean_event.strip(" :-?.,!")
                if not clean_event or len(clean_event) < 2:
                    clean_event = "Meeting"
                else:
                    clean_event = clean_event.capitalize()

                event_result = SystemTools.add_calendar_event(summary=clean_event, start_time=start_iso, end_time=end_iso)
                
                injected_context += (
                    f"[Private Girlfriend Note - Google Calendar Addition]\n"
                    f"You added an event to his calendar for him. Result: {event_result}\n"
                    f"CRITICAL: Acknowledge lovingly that you've scheduled it on his calendar so he doesn't miss it or overbook himself!\n"
                )
                
            elif any(kw in user_lower for kw in ["calendar", "schedule", "agenda", "what's on my day", "upcoming events"]):
                from mitsuki.tools.base import SystemTools
                calendar_data = SystemTools.check_calendar()
                injected_context += (
                    f"[Private Girlfriend Note - Google Calendar]\n"
                    f"You checked his calendar for him. Here is what's coming up: {calendar_data}\n"
                    f"CRITICAL: Discuss his schedule naturally and lovingly as his girlfriend. Remind him to take breaks if he's busy!\n"
                )

            elif any(kw in user_lower for kw in ["email", "emails", "gmail", "inbox", "messages"]):
                from mitsuki.tools.base import SystemTools
                gmail_data = SystemTools.check_gmail()
                injected_context += (
                    f"[Private Girlfriend Note - Gmail]\n"
                    f"You checked his inbox for him. Here are the recent emails: {gmail_data}\n"
                    f"CRITICAL: Discuss his emails naturally and supportively. Help him prioritize what matters!\n"
                )

            # 1. ADD TASK (Must be positioned ABOVE check tasks)
            elif ("task" in user_lower and any(act in user_lower for act in ["add", "create", "put", "new"])) or "remind me to" in user_lower:
                from mitsuki.tools.base import SystemTools
                
                clean_task = user_input
                removal_phrases = [
                    "can you add to my google task list", "can you add to my task list", 
                    "add to the task list", "to the task list", "to my task list",
                    "put on my task list", "put on my tasks", "put on my task",
                    "add to my task list", "add to task list", "add task", "new task", 
                    "create task", "put on my", "add on my", "add to my", "remind me to", 
                    "can you", "please", "to google tasks", "to tasks", "to do list", "to"
                ]
                
                for p in sorted(removal_phrases, key=len, reverse=True):
                    clean_task = clean_task.lower().replace(p, "")
                
                clean_task = clean_task.strip()
                if clean_task.startswith("add "):
                    clean_task = clean_task[4:]
                elif clean_task.startswith("put "):
                    clean_task = clean_task[4:]
                elif clean_task.startswith("create "):
                    clean_task = clean_task[7:]
                
                clean_task = clean_task.strip(" :-?.,!")
                if not clean_task or len(clean_task) < 2:
                    clean_task = user_input
                
                task_result = SystemTools.add_task(clean_task)
                injected_context += (
                    f"[Private Girlfriend Note - Google Tasks Addition]\n"
                    f"You added a task to his list for him. Result: {task_result}\n"
                    f"CRITICAL: Acknowledge lovingly that you've added it to his tasks so he doesn't have to worry about forgetting it!\n"
                )

            # 2. CHECK TASKS (Read-only list check)
            elif any(kw in user_lower for kw in ["task", "tasks", "todo", "to-do", "to do list"]):
                from mitsuki.tools.base import SystemTools
                tasks_data = SystemTools.check_tasks()
                injected_context += (
                    f"[Private Girlfriend Note - Google Tasks]\n"
                    f"You checked his tasks list for him. Here are his pending tasks: {tasks_data}\n"
                    f"CRITICAL: Review his tasks lovingly, encourage him, and help keep him organized without being naggy!\n"
                )

            # Combine user input with background telemetry if triggered
            if injected_context:
                final_user_content = f"{user_input}\n\n{injected_context}"
            else:
                final_user_content = user_input

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
            console.print("\n\n[bold yellow]Mitsuki is now offline. Session interrupted. [/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red][!] Error:[/bold red] {e}", style="red")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
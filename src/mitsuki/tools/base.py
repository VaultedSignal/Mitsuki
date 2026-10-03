import subprocess
import platform
import psutil
import httpx
from typing import Dict, Any
from ddgs import DDGS
from bs4 import BeautifulSoup
from typing import Optional


class SystemTools:
    """A collection of safe local environment tools for Mitsuki."""

    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Check current local CPU, RAM, and disk utilization."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "os": platform.system(),
            "cpu_usage_percent": cpu_usage,
            "ram_usage_percent": memory.percent,
            "ram_available_gb": round(memory.available / (1024**3), 2),
            "disk_usage_percent": disk.percent
        }

    @staticmethod
    def list_project_directory(path: str = ".") -> str:
        """List files and folders in a local project directory to see what you're working on."""
        import os
        try:
            items = os.listdir(path)
            # Filter out hidden or virtual environment folders for cleanliness
            filtered = [item for item in items if not item.startswith('.') and item != "__pycache__"]
            return f"Visible items in {path}: {', '.join(filtered)}"
        except Exception as e:
            return f"Error reading directory: {str(e)}"

    @staticmethod
    def read_file_content(file_path: str, max_chars: int = 4000) -> str:
        """Read the contents of a specific text/code file within the workspace."""
        import os
        try:
            # Basic safety check to prevent directory traversal outside the workspace
            normalized_path = os.path.normpath(file_path)
            if normalized_path.startswith("..") or os.path.isabs(file_path):
                return "Error: Access denied. Cannot read files outside the project directory."
            
            if not os.path.exists(normalized_path):
                return f"Error: File '{file_path}' not found."

            with open(normalized_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(max_chars)
                if len(content) == max_chars:
                    content += "\n[Content truncated due to length...]"
                return f"Contents of {file_path}:\n```\n{content}\n```"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def check_running_processes() -> str:
        """Check for active gaming or media applications running on the system."""
        target_processes = {
            "minecraft.exe": "Minecraft",
            "javaw.exe": "Minecraft (Java)",
            "vlc.exe": "VLC Media Player",
            "spotify.exe": "Spotify",
            "discord.exe": "Discord",
            "code.exe": "Visual Studio Code"
        }
        
        active_apps = []
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info.get('name')
                if name:
                    name_lower = name.lower()
                    for proc_key, app_label in target_processes.items():
                        if proc_key in name_lower and app_label not in active_apps:
                            active_apps.append(app_label)
                            
            if active_apps:
                return f"Currently active monitored applications on my PC: {', '.join(active_apps)}."
            else:
                return "No major monitored gaming or media apps are currently active."
        except Exception as e:
            return f"Error checking processes: {str(e)}"

    @staticmethod
    def web_search(query: str, max_results: int = 10) -> str:
        """Perform a quick web search using ddgs."""
        try:
            results = []
            with DDGS() as client:
                search_gen = client.text(query, max_results=max_results)
                if search_gen:
                    for r in search_gen:
                        results.append(r)
            
            if not results:
                return "No relevant web search results found."
            
            formatted = "[Live Internet Search Findings]\n"
            for r in results:
                formatted += f"- {r.get('title')}: {r.get('body')}\n"
            return formatted
        except Exception as e:
            return f"Error performing web search: {e}"

    #Half decent scraper
    @staticmethod
    def scrape_web_page(url: str, max_chars: int = 4000) -> str:
        """Fetch and parse clean text content from a given URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            with httpx.Client(follow_redirects=True, timeout=10.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

                # Parse HTML content
                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script, style, nav, and footer elements to reduce clutter
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()

                # Extract readable text
                text = soup.get_text(separator="\n", strip=True)
                
                if len(text) > max_chars:
                    text = text[:max_chars] + "\n[Content truncated due to length...]"

                return f"Contents of URL ({url}):\n{text}"
        except Exception as e:
            return f"Error scraping web page: {e}"

    #Google intergrations
    @staticmethod
    def check_calendar() -> str:
        from mitsuki.tools.google_calendar import GoogleCalendarTool
        return GoogleCalendarTool.get_upcoming_events()

    @staticmethod
    def check_gmail() -> str:
        """Fetches recent emails from Gmail."""
        from mitsuki.tools.google_gmail import GoogleGmailTool
        return GoogleGmailTool.get_recent_emails()

    @staticmethod
    def check_tasks() -> str:
        """Fetches pending items from Google Tasks."""
        from mitsuki.tools.google_tasks import GoogleTasksTool
        return GoogleTasksTool.get_pending_tasks()

    @staticmethod
    def add_task(task_title: str) -> str:
        """Adds a new task to Google Tasks."""
        from mitsuki.tools.google_tasks import GoogleTasksTool
        return GoogleTasksTool.create_task(task_title)

    @staticmethod
    def add_calendar_event(summary: str, start_time: str, end_time: Optional[str] = None) -> str:
        """Adds a new event to Google Calendar."""
        from mitsuki.tools.google_calendar import GoogleCalendarTool
        return GoogleCalendarTool.create_event(summary, start_time, end_time)   
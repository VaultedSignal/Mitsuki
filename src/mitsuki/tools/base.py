import subprocess
import platform
import psutil
from typing import Dict, Any

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
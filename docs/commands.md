# Mitsuki Commands & Tool Reference

This document outlines the available interactive terminal commands and natural language triggers built into Mitsuki.

## 1. Terminal Commands
Type these directly into the terminal prompt during an active session:

* **`/stats`**
  * **Action:** Fetches live hardware metrics via `psutil` (OS, CPU usage percentage, RAM usage percentage, available RAM in GB, and disk usage percentage).
  * **Behavior:** Injects the metrics into Mitsuki's context so she can comment on your workload and check in on you.

* **`/files`**
  * **Action:** Scans the active project working directory, filtering out hidden files and caches.
  * **Behavior:** Feeds the visible file list into her context so she can review what you're coding or building.

* **`/clear`**
  * **Action:** Clears the active chat session history, resets the screen, and provides a fresh slate.

* **`/help`**
  * **Action:** Displays the interactive help menu listing active commands.

* **`/exit` or `/quit`**
  * **Action:** Safely terminates the interactive session and exits the terminal loop.

---

## 2. Natural Language Context Injection
Mitsuki is equipped with lightweight intent triggers. You don't always have to use slash commands; she can dynamically grab context when you bring up specific topics naturally:

* **PC & Hardware Triggers:** 
  * *Keywords:* `pc`, `stats`, `computer`, `cpu`, `ram`
  * *Behavior:* Automatically captures a fresh snapshot of your system metrics and injects them into her prompt response window.
* **Workspace & Project Triggers:** 
  * *Keywords:* `files`, `project`, `folder`, `workspace`, `code`
  * *Behavior:* Automatically scans your project directory files and injects the file list into her prompt window.
* **File Reading Triggers:**
  * *Keywords:* `read`, `inspect`, `code in`, `show me` (combined with a file path like `main.py` or `base.py`)
  * *Behavior:* Automatically reads the contents of the specified text/code file and injects it into her context so she can review your code line-by-line.
* **Gaming & Media Activity Triggers:**
  * *Keywords:* `playing`, `game`, `minecraft`, `listening`, `music`, `spotify`, `discord`, `running`
  * *Behavior:* Automatically scans background processes to see if games or media players are open, allowing Mitsuki to comment on your leisure activities.
# Mitsuki

Mitsuki is a decoupled, modular, and locally hosted AI companion framework. Designed with a model-agnostic architecture, she runs entirely on your local hardware via Ollama, combining deep emotional presence, a grounded late-20s personality, and a clean command-line interface.

## Features
- **Local & Private:** Runs entirely offline on your hardware using Ollama (optimized for high-performance GPUs like the RTX 5080).
- **Decoupled Architecture:** Clean separation between the core conversation manager, provider abstractions, system prompts, and user interface.
- **Tuned Personality:** A mature, witty, and warm companion framework inspired by classic anime archetypes—strictly free of meta-commentary, code-referencing, or awkward roleplay stage directions.
- **Extensible Framework:** Designed for modular expansion (persistent memory, tool use, and advanced context features).

## Project Structure
- `src/mitsuki/core/` - Conversation management and message looping.
- `src/mitsuki/llm/` - Provider abstraction layer for Ollama and local LLMs.
- `docs/` - Design specs and personality framework documentation.
- `tests/` - Unit tests verifying backend functionality via `pytest`.

## Getting Started

1. **Clone the repository:**
   ```powershell
   git clone [https://github.com/VaultedSignal/Mitsuki.git](https://github.com/VaultedSignal/Mitsuki.git)
   cd Mitsuki
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install -r requirements.txt
   ```

2. **Ensure Ollama is running & pull a model:**
   Make sure your local Ollama server is active, then pull a compatible model like Llama 3.1:
   ```powershell
   ollama pull llama3.1
   ```

3. **Launch Mitsuki:**
   ```powershell
   python -m mitsuki.main
   ```
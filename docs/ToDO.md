### Mitsuki Master Roadmap

#### Phase 0 — Foundation (Complete)
* [x] Development environment setup & virtual environment (.venv)
* [x] GitHub repository initialization & version control (`VaultedSignal/Mitsuki`)
* [x] Modern Python project definition (`pyproject.toml`)
* [x] Configuration handling (`.env` / settings)
* [x] Basic application startup (`python -m mitsuki.main`)

#### Phase 1 — Text AI & Core CLI (Complete)
* [x] Model-agnostic LLM provider abstraction layer (`src/mitsuki/llm/`)
* [x] Local LLM integration via Ollama (configured for Llama 3.1/8b)
* [x] Conversation manager & message history sliding window (`src/mitsuki/core/`)
* [x] Personality system & system prompt framework (`docs/personality.md`)
* [x] Polished Rich terminal CLI interface with custom color-coded input/output panels

#### Phase 2 — Persistent Memory & Context Management (Complete)
* [x] Local SQLite database storage backend (`data/mitsuki.db`)
* [x] Short-term session chat history logging across terminal restarts
* [x] Long-term structured memory / Fact extraction ("Journal")
* [x] Automated background LLM fact extraction hook during conversation
* [x] Dynamic memory context injection into the system prompt

#### Phase 3 — Advanced Tool Use & Local Environment Integration (Complete)
* [x] Tool framework architecture (`src/mitsuki/tools/`)
* [x] Live system hardware metrics (`/stats` & natural language CPU/RAM checks)
* [x] Project workspace directory scanning (`/files`)
* [x] Deep file content reading & code review (.py, .md, etc.)
* [x] Interactive process monitoring (background detection of active apps, games, and IDEs)

#### Phase 3.5 — Connected Tools & APIs (Current)
* [x] **Internet Search Tool:** Web search integration (DuckDuckGo) for live information lookup
* [x] **Web Page Scraper Tool:** Fetching and parsing text content from URLs on the fly
* [x] **Google OAuth2 Authentication Module:** Secure local credential management for Google APIs
* [x] **Google Calendar Integration:** Checking schedules, adding events, and reminding you of upcoming meetings
* [x] **Gmail Integration:** Reading unread messages, drafting replies, and summarizing your inbox
* [x] **Google Tasks Integration:** Managing to-do lists and tracking action items
* [x] **Gateways:** Lightweight bot hooks for Discord

#### Code Hygiene & Refactoring:**
* [ ]  Simplifying core logic, removing duplicates, cleaning up old structures, and adding comprehensive comments
* [ ] **Performance Optimization:** Making execution faster, snappier, and cleaner
* [ ] make her update live


#### Phase 4 — Interface Evolution (Immersion, Voice, Live2D)
* [x] Immersive terminal startup and clean window layout
* [ ] **Screen Capture & Multimodal Perception:** Allowing Mitsuki to "see" your monitor/active windows (e.g., watching anime or reviewing code together)
* [ ] **Text-to-Speech (TTS) & Speech-to-Text (STT):** Emotional speech output and voice input integration
* [ ] **Live2D Desktop Avatar:** Visual companion model with dynamic expressions and idle animations

#### Phase 5 — Autonomous Behavior & Proactive Intelligence
* [ ] **Emotional State Engine:** Mood tracking and dynamic personality shifts based on interactions
* [ ] **Activity State & Context Awareness:** Proactive background checks and situational awareness
* [ ] **Autonomous Proactive Messaging:** Allowing Mitsuki to message you unprompted after periods of inactivity or when system state changes
* [ ] **Idle Behavior / Ambient AI:** Self-directed background routines
* [ ] **Decision-Maker Engine:** Autonomous background evaluation where the LLM decides when to invoke tools on its own

#### Phase 6 — Omnichannel Expansion & Mobile
* [ ] **Mobile Integration / Remote Access:** Bridging core memory and personality to mobile platforms
* [ ] **Advanced Cloud / Remote Syncing:** Optional cross-device conversation synchronization

#### Phase 7 — Interactive Gaming & Shared Experiences
* [ ] **Shared Activity Framework:** Specialized integrations for co-op games (like Minecraft integration for building and playing together)
* [ ] **Media & Entertainment Sync:** Watching movies/anime or listening to music in sync with live commentary
* [ ] **Mini-games & Interactive Events:** In-chat games played directly with Mitsuki
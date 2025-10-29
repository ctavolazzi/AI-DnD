# 🎯 AI-DnD Codebase Action Plan
**Based on Comprehensive Review - October 29, 2025**

> This action plan consolidates the findings from the complete codebase review into a prioritized, executable roadmap.

---

## 📊 Executive Summary

**Current State:** Advanced Beta / Early Production (⭐⭐⭐⭐)
**Target State:** Production Ready (⭐⭐⭐⭐⭐)
**Estimated Effort:** 4-6 weeks of focused development
**Priority Areas:** Organization, Standardization, Testing, Documentation

---

## 🚨 Critical Issues (Fix First)

### Issue 1: Data Model Inconsistencies
**Impact:** HIGH - Causes runtime errors and confusion
**Effort:** MEDIUM (2-3 days)
**Priority:** 🔴 CRITICAL

**Problem:**
- 3 incompatible `Character` class definitions
- 2 incompatible `Location` class definitions
- Inventory system not integrated

**Solution:**
```bash
# 1. Create unified models (Day 1)
mkdir -p src/models/
touch src/models/character.py
touch src/models/location.py
touch src/models/inventory.py

# 2. Define canonical implementations (Day 1-2)
# - character.py: Single Character class with all features
# - location.py: Single Location class
# - inventory.py: Integrate with Character

# 3. Update all imports (Day 2-3)
# - Search: grep -r "class Character" --include="*.py"
# - Replace with imports from src/models/

# 4. Run migration tests (Day 3)
pytest tests/unit/test_models.py
```

**Files to Consolidate:**
- `dnd_game.py` → `Character` class
- `character_state.py` → `Character` class
- `backend/app/models/character.py` → `Character` class
- **Action:** Merge into single `src/models/character.py`

### Issue 2: Multiple Incompatible Entry Points
**Impact:** HIGH - User confusion, maintenance burden
**Effort:** MEDIUM (2-3 days)
**Priority:** 🔴 CRITICAL

**Problem:**
- 10+ different entry points
- No clear "main" way to start the game
- Duplicated initialization logic

**Solution:**
```bash
# Create unified entry point
touch main.py

# Content:
"""
AI-DnD Unified Entry Point
Choose your adventure mode:
1. Story Theater (web-based narrative)
2. Retro Adventure (classic RPG)
3. Character Generator
4. Pygame Interactive
5. CLI Mode
"""

# Deprecate old entry points
mkdir -p legacy/entry_points/
git mv run_game.py legacy/entry_points/
git mv pygame_dnd_game.py legacy/entry_points/
# ... etc
```

### Issue 3: In-Memory Session Storage
**Impact:** HIGH - Data loss on restart
**Effort:** MEDIUM (2-3 days)
**Priority:** 🔴 CRITICAL

**Problem:**
- Flask servers use global dictionaries
- Sessions lost on restart
- No persistence across servers

**Solution:**
```python
# Implement shared session storage
# Option A: Redis (recommended)
pip install redis

# backend/app/services/session_store.py
import redis
import json

class SessionStore:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def save_session(self, session_id, data):
        self.redis.set(f"session:{session_id}", json.dumps(data))

    def get_session(self, session_id):
        data = self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None

# Option B: SQLite (simpler, no extra service)
# Use existing FastAPI database pattern
```

**Implementation Steps:**
1. Choose storage backend (Redis or SQLite)
2. Create `SessionStore` class
3. Update all servers to use `SessionStore`
4. Add session expiry (24 hours)
5. Test session recovery after restart

---

## 🔴 High Priority (Week 1-2)

### 1. Root Directory Reorganization
**Effort:** 3-4 days
**Impact:** Major improvement in maintainability

**Current Problem:**
```
AI-DnD/
├── 50+ Python files at root
├── 29 HTML files at root
├── 50+ Markdown files at root
└── Difficult to navigate
```

**Target Structure:**
```
AI-DnD/
├── src/
│   ├── servers/
│   │   ├── narrative_server.py
│   │   ├── image_server.py
│   │   └── persona_server.py
│   ├── core/
│   │   ├── game_engine.py
│   │   ├── narrative_engine.py
│   │   └── character_generator.py
│   ├── models/
│   │   ├── character.py (UNIFIED)
│   │   ├── location.py (UNIFIED)
│   │   ├── inventory.py
│   │   └── session.py
│   └── utils/
│       ├── logging.py
│       ├── exceptions.py
│       └── validation.py
├── frontends/
│   ├── story-theater/
│   ├── retro-adventure/
│   ├── character-dashboard/
│   └── shared/
│       ├── api-client.js
│       └── components.js
├── docs/
│   ├── README.md
│   ├── getting-started/
│   ├── architecture/
│   ├── api/
│   └── features/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/
│   ├── settings.py
│   └── environments/
├── scripts/
│   └── setup.sh
└── main.py (UNIFIED ENTRY POINT)
```

**Migration Script:**
```bash
#!/bin/bash
# migrate_structure.sh

echo "🚀 Starting directory reorganization..."

# Create new structure
mkdir -p src/{servers,core,models,utils}
mkdir -p frontends/{story-theater,retro-adventure,character-dashboard,shared}
mkdir -p docs/{getting-started,architecture,api,features}
mkdir -p tests/{unit,integration,e2e}
mkdir -p config/environments

# Move Python servers
echo "📦 Moving servers..."
mv dnd_narrative_server.py src/servers/narrative_server.py
mv nano_banana_server.py src/servers/image_server.py
mv persona_dossier_server.py src/servers/persona_server.py

# Move core game files
echo "🎮 Moving core files..."
mv dnd_game.py src/core/game_engine.py
mv narrative_engine.py src/core/narrative_engine.py
mv character_generator_core.py src/core/character_generator.py

# Move HTML frontends
echo "🌐 Moving frontends..."
mv interactive-story-theater.html frontends/story-theater/index.html
mv retro-adventure-game.html frontends/retro-adventure/index.html
mv character_dashboard.html frontends/character-dashboard/index.html

# Move tests
echo "🧪 Moving tests..."
mv test_*.py tests/unit/

# Move documentation
echo "📚 Moving documentation..."
mv *_README.md docs/features/
mv *_COMPLETE.md docs/archive/

# Update imports
echo "🔧 Updating imports..."
find . -type f -name "*.py" -exec sed -i '' 's/from dnd_game import/from src.core.game_engine import/g' {} +
find . -type f -name "*.py" -exec sed -i '' 's/from narrative_engine import/from src.core.narrative_engine import/g' {} +

echo "✅ Migration complete!"
echo "⚠️  Please verify imports and run tests"
```

### 2. Standardize Error Handling
**Effort:** 2 days
**Impact:** Better debugging and reliability

**Implementation:**
```python
# src/utils/exceptions.py
class DnDException(Exception):
    """Base exception for AI-DnD."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self):
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }

class NarrativeGenerationError(DnDException):
    """Failed to generate narrative."""
    pass

class ImageGenerationError(DnDException):
    """Failed to generate image."""
    pass

class GameStateError(DnDException):
    """Invalid game state."""
    pass

class SessionNotFoundError(DnDException):
    """Session does not exist."""
    pass

class CharacterError(DnDException):
    """Character-related error."""
    pass

# Usage in servers
from src.utils.exceptions import NarrativeGenerationError

try:
    narrative = generate_narrative(prompt)
except Exception as e:
    raise NarrativeGenerationError(
        "Failed to generate narrative",
        details={"prompt": prompt, "error": str(e)}
    )
```

**Migration Steps:**
1. Create exception hierarchy
2. Update all server error handling
3. Standardize error responses
4. Add error logging
5. Update frontend error displays

### 3. Comprehensive Test Suite
**Effort:** 4-5 days
**Impact:** Confidence in changes, fewer bugs

**Target Coverage:** >80% for core modules

**Test Structure:**
```
tests/
├── unit/
│   ├── test_character.py         # Character model tests
│   ├── test_location.py          # Location model tests
│   ├── test_inventory.py         # Inventory tests
│   ├── test_narrative_engine.py  # Narrative generation tests
│   ├── test_combat.py            # Combat mechanics tests
│   └── test_game_engine.py       # Core game tests
├── integration/
│   ├── test_narrative_server.py  # Narrative API tests
│   ├── test_image_server.py      # Image API tests
│   ├── test_fastapi_backend.py   # FastAPI tests
│   └── test_session_persistence.py # Session storage tests
├── e2e/
│   ├── test_story_theater_flow.py    # Full Story Theater workflow
│   ├── test_character_creation.py    # Character creation workflow
│   └── test_retro_game_flow.py       # Retro adventure workflow
└── fixtures/
    ├── sample_characters.json
    ├── sample_locations.json
    └── sample_narratives.json
```

**Example Test:**
```python
# tests/unit/test_character.py
import pytest
from src.models.character import Character

class TestCharacter:
    def test_create_character(self):
        char = Character(
            name="Aldric",
            char_class="Wizard",
            level=1
        )
        assert char.name == "Aldric"
        assert char.char_class == "Wizard"
        assert char.hp > 0

    def test_take_damage(self):
        char = Character(name="Test", char_class="Fighter", level=1)
        initial_hp = char.hp
        char.take_damage(10)
        assert char.hp == initial_hp - 10

    def test_death(self):
        char = Character(name="Test", char_class="Fighter", level=1)
        char.take_damage(999)
        assert not char.alive
        assert char.hp == 0

    def test_inventory_integration(self):
        char = Character(name="Test", char_class="Fighter", level=1)
        char.add_item("Sword", quantity=1)
        assert "Sword" in char.inventory
        assert char.inventory["Sword"] == 1
```

### 4. Documentation Consolidation
**Effort:** 2 days
**Impact:** Easier onboarding, better discoverability

**Current:** 50+ MD files at root + docs/
**Target:** All docs in docs/ with clear navigation

**Migration:**
```bash
# Organize by category
mkdir -p docs/{getting-started,architecture,api,features,development,archive}

# Move files
mv *_README.md docs/features/
mv *_COMPLETE.md docs/archive/
mv *_PLAN.md docs/architecture/
mv QUICK_START*.md docs/getting-started/

# Create master index
cat > docs/README.md << 'EOF'
# AI-DnD Documentation

## Quick Links
- [Getting Started](getting-started/installation.md)
- [Architecture Overview](architecture/system-overview.md)
- [API Reference](api/README.md)
- [Features Guide](features/README.md)

## Table of Contents

### Getting Started
- Installation
- Quick Start
- Configuration
- First Adventure

### Architecture
- System Overview
- Backend Services
- Frontend Applications
- Data Models

### API Reference
- Narrative Server API
- Image Generation API
- FastAPI Endpoints
- MCP Servers

### Features
- Story Theater
- Character Generation
- Image Generation
- Obsidian Integration

### Development
- Contributing
- Testing Guide
- Code Standards
- Deployment
EOF
```

---

## 🟡 Medium Priority (Week 3-4)

### 5. Centralize Configuration
**Effort:** 2 days

**Create unified config system:**
```python
# config/settings.py
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings with validation."""

    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    pixellab_api_key: str = Field(None, env="PIXELLAB_API_KEY")

    # Server Ports
    narrative_server_port: int = 5002
    image_server_port: int = 5000
    fastapi_port: int = 8000

    # Paths
    obsidian_vault_path: str = Field("./ai-dnd-test-vault")
    image_storage_path: str = Field("./images")

    # AI Models
    default_ai_model: str = "gemini"
    ollama_fallback: bool = True

    # Rate Limiting
    max_requests_per_minute: int = 10

    # Session Management
    session_expiry_hours: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = False

# Usage
from config.settings import Settings
settings = Settings()
```

### 6. Create Shared Frontend Components
**Effort:** 3 days

**Shared API Client:**
```javascript
// frontends/shared/api-client.js
export class DnDAPIClient {
    constructor() {
        this.baseURLs = {
            narrative: 'http://localhost:5002',
            image: 'http://localhost:5000',
            game: 'http://localhost:8000'
        };
    }

    async request(service, endpoint, options = {}) {
        const url = `${this.baseURLs[service]}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new APIError(error.message, error.details);
        }

        return response.json();
    }

    // Narrative endpoints
    async startSession(theme) {
        return this.request('narrative', '/start-session', {
            method: 'POST',
            body: JSON.stringify({ theme })
        });
    }

    async generateChapter(sessionId, userInput) {
        return this.request('narrative', '/generate-chapter', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId, user_input: userInput })
        });
    }

    // Image endpoints
    async generateImage(prompt) {
        return this.request('image', '/generate', {
            method: 'POST',
            body: JSON.stringify({ prompt })
        });
    }
}

// Shared error handling
export class APIError extends Error {
    constructor(message, details) {
        super(message);
        this.name = 'APIError';
        this.details = details;
    }
}
```

### 7. Implement Structured Logging
**Effort:** 2 days

```python
# src/utils/logging.py
import logging
import json
from pathlib import Path
from datetime import datetime

class StructuredLogger:
    """JSON-structured logging for better observability."""

    def __init__(self, name: str, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # File handler with JSON formatting
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        fh = logging.FileHandler(log_dir / f"{name}.json")
        fh.setFormatter(self.JSONFormatter())

        # Console handler with readable formatting
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }

            if hasattr(record, 'user_id'):
                log_data['user_id'] = record.user_id
            if hasattr(record, 'session_id'):
                log_data['session_id'] = record.session_id

            return json.dumps(log_data)

    def info(self, message, **context):
        extra = {k: v for k, v in context.items()}
        self.logger.info(message, extra=extra)

    def error(self, message, **context):
        extra = {k: v for k, v in context.items()}
        self.logger.error(message, extra=extra)

# Usage
from src.utils.logging import StructuredLogger

logger = StructuredLogger('narrative_server')
logger.info("Session started", session_id="abc123", user_id="user456")
```

### 8. Add Performance Monitoring
**Effort:** 2 days

```python
# src/utils/performance.py
import time
from functools import wraps
from src.utils.logging import StructuredLogger

logger = StructuredLogger('performance')

def monitor_performance(func):
    """Decorator to monitor function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(
                f"{func.__name__} completed",
                function=func.__name__,
                duration_seconds=duration,
                status="success"
            )

            return result
        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                f"{func.__name__} failed",
                function=func.__name__,
                duration_seconds=duration,
                status="error",
                error=str(e)
            )

            raise

    return wrapper

# Usage
@monitor_performance
def generate_narrative(prompt):
    # ... generation logic
    pass
```

---

## 🟢 Low Priority (Week 5-6)

### 9. Docker Support
**Effort:** 2 days

```dockerfile
# Dockerfile.narrative
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

CMD ["python", "-m", "src.servers.narrative_server"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  narrative-server:
    build:
      context: .
      dockerfile: Dockerfile.narrative
    ports:
      - "5002:5002"
    env_file:
      - .env
    depends_on:
      - redis

  image-server:
    build:
      context: .
      dockerfile: Dockerfile.image
    ports:
      - "5000:5000"
    env_file:
      - .env

  fastapi-backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: aidnd
      POSTGRES_USER: aidnd
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 10. CI/CD Pipeline
**Effort:** 2 days

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 11. Type Hints & Type Checking
**Effort:** 3 days

```python
# Add type hints to all functions
from typing import Optional, Dict, List, Union

def generate_narrative(
    prompt: str,
    context: Optional[List[str]] = None,
    max_length: int = 500
) -> Dict[str, Union[str, int]]:
    """Generate narrative text from prompt.

    Args:
        prompt: The generation prompt
        context: Previous narrative context
        max_length: Maximum response length

    Returns:
        Dictionary with 'text', 'tokens', 'model' keys

    Raises:
        NarrativeGenerationError: If generation fails
    """
    pass
```

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[mypy-tests.*]
disallow_untyped_defs = False
```

### 12. Add Development Makefile
**Effort:** 1 day

```makefile
# Makefile
.PHONY: help setup install test run clean docker

help:
	@echo "AI-DnD Development Commands"
	@echo "  make setup      - Initial project setup"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run test suite"
	@echo "  make run        - Start all servers"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make docker     - Build and run Docker containers"

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp config_template.env .env
	@echo "✅ Setup complete! Edit .env with your API keys"

install:
	pip install -r requirements.txt
	pip install -r requirements/dev.txt

test:
	pytest tests/ -v --cov=src

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

run-narrative:
	python -m src.servers.narrative_server

run-image:
	python -m src.servers.image_server

run-backend:
	cd backend && uvicorn app.main:app --reload

run:
	@echo "Starting all servers..."
	@./scripts/start_all.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/

docker:
	docker-compose up --build
```

---

## 📅 Implementation Timeline

### Week 1: Critical Fixes
- **Day 1-2:** Data model consolidation
- **Day 3-4:** Unified entry point
- **Day 5:** Session persistence

### Week 2: Organization
- **Day 1-3:** Root directory reorganization
- **Day 4-5:** Error handling standardization

### Week 3: Quality
- **Day 1-3:** Comprehensive test suite
- **Day 4-5:** Documentation consolidation

### Week 4: Refinement
- **Day 1-2:** Centralized configuration
- **Day 3-5:** Shared frontend components

### Week 5-6: Polish
- **Day 1-2:** Structured logging
- **Day 3-4:** Performance monitoring
- **Day 5-6:** Docker support
- **Week 6:** CI/CD pipeline

---

## ✅ Success Criteria

### After Critical Fixes (Week 1)
- ✅ Single Character class used everywhere
- ✅ Single Location class used everywhere
- ✅ Clear entry point (main.py)
- ✅ Sessions persist across restarts

### After High Priority (Week 2)
- ✅ Clean directory structure
- ✅ Consistent error handling
- ✅ Comprehensive test coverage
- ✅ Organized documentation

### After Medium Priority (Week 3-4)
- ✅ Centralized configuration
- ✅ Shared frontend code
- ✅ Structured logging
- ✅ Performance metrics

### After Low Priority (Week 5-6)
- ✅ Docker deployment ready
- ✅ CI/CD pipeline running
- ✅ Type checking enabled
- ✅ Development automation

---

## 📊 Metrics to Track

### Code Quality
- [ ] Test coverage >80%
- [ ] No critical linter errors
- [ ] Type hints on all functions
- [ ] Documentation coverage >90%

### Performance
- [ ] API response time <2s (p95)
- [ ] Image generation <10s (p95)
- [ ] Memory usage <500MB per server
- [ ] Session recovery <100ms

### Organization
- [ ] <10 files at root
- [ ] All tests in tests/
- [ ] All docs in docs/
- [ ] Clear module structure

### Developer Experience
- [ ] One-command setup (`make setup`)
- [ ] One-command run (`make run`)
- [ ] One-command test (`make test`)
- [ ] Clear contribution guide

---

## 🔧 Tools & Scripts

### Quick Migration Helper
```bash
# scripts/quick_migrate.sh
#!/bin/bash

echo "🚀 Quick Migration Script"
echo "This will reorganize your codebase"
read -p "Continue? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Run full migration
    ./scripts/migrate_structure.sh
    ./scripts/update_imports.sh
    ./scripts/move_tests.sh
    ./scripts/consolidate_docs.sh

    echo "✅ Migration complete!"
    echo "⚠️  Please run: make test"
fi
```

### Import Updater
```bash
# scripts/update_imports.sh
#!/bin/bash

echo "🔧 Updating imports..."

# Update Character imports
find . -type f -name "*.py" ! -path "./venv/*" ! -path "./legacy/*" \
    -exec sed -i '' 's/from dnd_game import Character/from src.models.character import Character/g' {} +

# Update Location imports
find . -type f -name "*.py" ! -path "./venv/*" ! -path "./legacy/*" \
    -exec sed -i '' 's/from dnd_game import Location/from src.models.location import Location/g' {} +

# Update NarrativeEngine imports
find . -type f -name "*.py" ! -path "./venv/*" ! -path "./legacy/*" \
    -exec sed -i '' 's/from narrative_engine import/from src.core.narrative_engine import/g' {} +

echo "✅ Imports updated"
```

### Test Runner
```bash
# scripts/run_all_tests.sh
#!/bin/bash

echo "🧪 Running all tests..."

# Unit tests
echo "📦 Unit tests..."
pytest tests/unit/ -v

# Integration tests
echo "🔗 Integration tests..."
pytest tests/integration/ -v

# E2E tests
echo "🌐 End-to-end tests..."
pytest tests/e2e/ -v

# Coverage report
echo "📊 Coverage report..."
pytest tests/ --cov=src --cov-report=html

echo "✅ All tests complete"
echo "📂 View coverage: open htmlcov/index.html"
```

---

## 🎯 Quick Wins (Start Here)

If you want to see immediate improvements, start with these:

### Quick Win 1: Create Unified Entry Point (30 min)
```python
# main.py
"""AI-DnD - Unified Entry Point"""

def show_menu():
    print("""
    🎲 AI-DnD - Choose Your Adventure

    1. Story Theater    - Interactive narrative with images
    2. Retro Adventure  - Classic RPG interface
    3. Character Gen    - Create D&D characters
    4. Pygame Mode      - Interactive pygame interface
    5. CLI Mode         - Command-line adventure

    0. Exit
    """)

    choice = input("Select mode (0-5): ")

    if choice == "1":
        import webbrowser
        webbrowser.open('frontends/story-theater/index.html')
    elif choice == "2":
        import webbrowser
        webbrowser.open('frontends/retro-adventure/index.html')
    # ... etc

if __name__ == "__main__":
    show_menu()
```

### Quick Win 2: Add .env.example (10 min)
```bash
# .env.example
# Copy this to .env and fill in your values

# Required API Keys
GEMINI_API_KEY=your_key_here

# Optional API Keys
PIXELLAB_API_KEY=your_key_here

# Server Configuration
NARRATIVE_SERVER_PORT=5002
IMAGE_SERVER_PORT=5000
FASTAPI_PORT=8000

# Paths
OBSIDIAN_VAULT_PATH=./ai-dnd-test-vault
IMAGE_STORAGE_PATH=./images

# AI Configuration
DEFAULT_AI_MODEL=gemini
OLLAMA_FALLBACK=true
```

### Quick Win 3: Add Makefile (15 min)
See Makefile example in Low Priority section above.

---

## 📞 Support & Questions

### Getting Help
- Review full codebase analysis: `_work_efforts_/10-19_development/10_core/10.31_20251029_codebase_review.md`
- Check documentation: `docs/README.md`
- Review work efforts: `_work_efforts_/devlog.md`

### Before Starting
1. Create a backup branch: `git checkout -b backup-before-refactor`
2. Commit current state: `git commit -am "Snapshot before refactoring"`
3. Run existing tests: `pytest tests/`
4. Document baseline metrics

### After Each Phase
1. Run test suite
2. Update documentation
3. Commit changes with descriptive message
4. Tag release: `git tag -a v1.0-refactor-phase1 -m "Phase 1 complete"`

---

## 🎉 Final Thoughts

This action plan transforms the comprehensive codebase review into concrete, achievable steps. The project already has a solid foundation - this plan focuses on organization, standardization, and polish to reach production readiness.

**Remember:**
- 🔴 Fix critical issues first (data models, persistence)
- 🟡 Then organize and standardize
- 🟢 Finally add polish and automation

**Estimated Total Effort:** 4-6 weeks
**End Result:** Production-ready, well-organized, maintainable codebase ⭐⭐⭐⭐⭐

---

**Plan Created:** October 29, 2025
**Based On:** Comprehensive Codebase Review
**Status:** Ready to Execute
**Next Step:** Start with Critical Issues (Week 1)


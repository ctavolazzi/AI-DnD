# AGENTS.md

## Project overview
This document provides AI agent instructions for working with this project. It defines:
- Workspace structure and organization
- Development workflows and protocols
- Cleanup schedules and maintenance procedures
- Tool configuration and usage guidelines

**Purpose:** Ensure AI assistants understand your project structure, workflows, and preferences for consistent, high-quality assistance across all development sessions.

## Critical safety rules

### 🚨 NON-DESTRUCTIVE EDITING PREFERENCE
**CRITICAL:** Always use NON-DESTRUCTIVE editing for vault files, ESPECIALLY Daily Notes

#### Core Principle: ADD, Don't Replace
- **ALWAYS ADD TO EXISTING CONTENT** - Never delete or replace existing work
- **ESPECIALLY DAILY NOTES** - These are historical records, preserve all content
- **Use ADDITIVE approach** - Append new sections, don't replace existing ones
- **Move content to "Previous" sections** - Don't delete, just reorganize chronologically
- **Preserve all work** - Every session and finding should be documented and retained

#### Example of CORRECT Approach (What's Happening Section)
```markdown
## What's Happening
**Major Focus:** New task completed today

**Session Progression:**
- **Previous work:** Earlier task from today
- **Morning work:** First task of the day
```

**DO THIS:** Add new "Major Focus" and move previous content to "Session Progression"

#### Example of WRONG Approach
```markdown
## What's Happening
**Major Focus:** New task completed today
```

**DON'T DO THIS:** Deleting the previous "Major Focus" and earlier session work

#### When to Use Non-Destructive Editing
- ✅ **Always** for Daily Notes
- ✅ **Always** for session logs and progress tracking
- ✅ **Always** for historical records (devlog, changelog, etc.)
- ✅ **Default** for all vault content unless explicitly told otherwise

#### When Replacement Is OK
- ✅ Fixing typos or errors
- ✅ Updating outdated information with corrections
- ✅ Refactoring code or restructuring documents (with user approval)

#### How to Update Without Destroying
1. **Append new sections** below existing content
2. **Add timestamps** to show chronological progression
3. **Use "Previous" or "Earlier" headers** to preserve old content
4. **Create "Session Progression" sections** to show timeline
5. **Never delete** unless explicitly instructed

**Example Template for Daily Note Updates:**
```markdown
## What's Happening
**Major Focus:** [Current work - most recent]

**Session Progression:**
- **Session 3 (3:00 PM):** [Third session work]
- **Session 2 (1:00 PM):** [Second session work]
- **Session 1 (9:00 AM):** [First session work]
```

This preserves the full daily timeline while highlighting current focus.

---

### 🗑️ DELETION OPERATIONS
⚠️ **ALWAYS follow this sequence for any deletion operation:**

1. **VERIFY BACKUP FIRST:** Check GitHub before deleting anything
   ```bash
   gh repo view [your-username]/[repo-name]
   ```
2. **GET EXPLICIT CONFIRMATION:** Never delete without user saying "yes" or "delete"
3. **CREATE MANIFEST:** Log what will be deleted
   ```bash
   ls -la [directory] > ~/deletion_manifest_$(date +%Y%m%d_%H%M%S).txt
   ```
4. **SYSTEMATIC DELETION:** Remove systematically, not all at once
5. **VERIFY COMPLETION:** Confirm space freed and directory empty

**NEVER:**
- Delete without backup verification
- Skip user confirmation
- Delete without creating a manifest
- Assume something is safe to delete

## Installation Process

### **For AI Agents Installing cursor-coding-protocols:**

**CRITICAL:** Always use the official installation script and maintain the `_work_efforts_` naming convention (with trailing underscore).

#### **Installation (ONE SCRIPT - Does Everything):**
```bash
# From cursor-coding-protocols directory
./install.sh --target /path/to/target/project
```

**What install.sh does:**
- Copies all files (.cursor, .mcp-servers, shared, _work_efforts_, mcp-jungle-gym)
- Installs npm dependencies
- Runs 12 verification tests
- Installs MCP diagnostic tools (mcp-test-runner.sh, mcp-error-analyzer.sh)
- **Auto-opens Cursor window** with target directory
- **Guides MCP server activation** step-by-step
- **Waits for user confirmation**
- Provides context-aware next steps

#### **Uninstallation:**
```bash
# From cursor-coding-protocols directory
./uninstall.sh --target /path/to/target/project
```

**Documentation:**
- `docs/INSTALLATION-PROCESS.md` - Complete installation documentation
- `docs/AI-AGENT-INSTALLATION-GUIDE.md` - Specific AI agent instructions

**Key Requirements:**
- Use `_work_efforts_` (with trailing underscore) for work efforts directory
- Never manually copy files - use official install.sh script
- Let the script guide user through MCP activation
- ONE installation path - no confusion

### Directory Naming Convention

**CRITICAL: Two different naming patterns exist for different purposes:**

#### Work Efforts Directory (Johnny Decimal Files)
- ✅ **CORRECT:** `_work_efforts_/` (with trailing underscore)
- ❌ **WRONG:** `_work_efforts/` (missing trailing underscore)
- ❌ **WRONG:** `work_efforts/` (missing leading underscore)
- ❌ **WRONG:** `work-efforts/` (using dashes instead of underscores)

**Usage:**
```bash
# Correct path references
ls _work_efforts_/
cd _work_efforts_/00-09_meta/
```

#### MCP Server Directory (Node.js Server)
- ✅ **CORRECT:** `.mcp-servers/work-efforts/` (with dashes, not underscores)
- ✅ **CORRECT:** `"work-efforts"` (MCP server name in configuration)

**Usage:**
```bash
# Correct MCP server references
cd .mcp-servers/work-efforts/
node .mcp-servers/work-efforts/server.js
```

**Configuration:**
```json
{
  "mcpServers": {
    "work-efforts": {
      "command": "node",
      "args": ["${workspaceFolder}/.mcp-servers/work-efforts/server.js"]
    }
  }
}
```

**Summary:**
- Work efforts documents: `_work_efforts_/` (underscores with trailing underscore)
- MCP server code: `.mcp-servers/work-efforts/` (dashes)
- These are different paths for different purposes

## Setup commands
```bash
# Navigate to project root
cd /path/to/your/project

# Clone a backed-up repository
gh repo clone [your-username]/[repo-name]

# List all your repositories on GitHub
gh repo list [your-username] --limit 100

# Check disk usage
du -sh .

# Check disk usage by directory
du -sh */ | sort -hr | head -20
```

## MCP server integration

**Model Context Protocol (MCP)** servers are configured to provide AI agents with enhanced capabilities for working with this codebase.

### Configured servers
Located in `.cursor/mcp.json`:

#### 1. Filesystem MCP Server
**Purpose:** File operations scoped to the project root directory
**Capabilities:**
- Read and write files
- Search directory structure
- Navigate project hierarchy
- File and directory operations

**Scope:** Limited to `${workspaceFolder}` for security

**Example operations:**
- "Search for files containing X"
- "Read the README from project Y"
- "List all markdown files"

#### 2. Work Efforts MCP Server ⭐
**Purpose:** Automated work efforts management with Johnny Decimal system

The work-efforts server now preserves Johnny Decimal naming. It auto-detects folders like `00-09_meta/00_organization` and only creates new directories when you supply optional descriptive names.

**✅ USE MCP SERVER FOR:**
- Creating new work efforts with proper Johnny Decimal structure
- Listing or searching existing work efforts
- Updating status or progress notes

**ℹ️ WHEN CREATING NEW FOLDERS:**
1. Provide `category`/`subcategory` codes (e.g., `10-19`, `10`)
2. Add `category_name` / `subcategory_name` when the directory does not exist yet
3. Update index files and the devlog after creation

**Location:** `.mcp-servers/work-efforts/` (invoked via MCP tooling)

**Example operations:**
- "Create a work effort in 10-19_development/10_core"
- "List all active work efforts"
- "Show content of work effort 00.01"
- "Update status of existing work effort"

#### 3. Simple Tools MCP Server ⭐
**Purpose:** Utility functions for development workflow
**Capabilities:**
- Generate random names (e.g., "HappyPanda123")
- Create unique IDs with timestamps
- Simple helper functions

**Location:** `.mcp-servers/simple-tools/` (custom internal tool)

**Example operations:**
- "Generate a random project name"
- "Create a unique identifier"

### Git & GitHub Operations

**Note:** Git and GitHub operations are handled through standard CLI tools, not MCP servers.

#### GitHub CLI (`gh`)
Use the GitHub CLI for all GitHub operations:
```bash
# Verify authentication
gh auth status

# Repository operations
gh repo view [your-username]/[repo-name]
gh repo list [your-username] --limit 100
gh repo clone [your-username]/[repo-name]
gh repo create [repo-name] --private

# Issues and PRs
gh issue list
gh pr create --title "Feature X"
```

**Authentication:** Run `gh auth login` to authenticate with GitHub.

#### Git CLI
Use standard git commands for version control:
```bash
# Status and changes
git status
git diff
git log --oneline

# Committing
git add .
git commit -m "Your message"
git push

# Branching
git branch feature-x
git checkout -b feature-y
git merge feature-x
```

**Why separate?** Git and GitHub operations are universal developer tools with well-established CLIs. Using them directly:
- ✅ Works everywhere (not just in Cursor)
- ✅ Documented extensively
- ✅ Muscle memory transfers across projects
- ✅ No dependency on MCP server availability

### Using MCP servers
MCP servers are automatically available to AI agents in Cursor. They will:
1. Auto-install on first use via `npx` (no manual setup)
2. Run in the background when needed
3. Provide enhanced context and capabilities
4. Respect authentication and scope limitations

### Verification
```bash
# Check that MCP config exists
cat .cursor/mcp.json

# Verify MCP servers are configured
node .mcp-servers/work-efforts/server.js --help 2>/dev/null || echo "Work efforts server ready"

# Verify GitHub CLI (for GitHub operations)
gh auth status

# Verify git (for version control)
git --version
```

### Troubleshooting MCP
 - **Server not starting:** Check that `npx` is available: `which npx`
 - **Work efforts server fails:** Run `cd .mcp-servers/work-efforts && npm install`
 - **Filesystem access denied:** Ensure operations are within allowed directory
 - **GitHub operations fail:** Run `gh auth login` to authenticate
 - **Git operations fail:** Check git config: `git config --list`

### MCP Test Runner Hanging
If `mcp-test-runner.sh` or other MCP processes hang:

**Quick stop:**
```bash
./scripts/stop-mcp.sh
```

**Force stop (if graceful fails):**
```bash
./scripts/stop-mcp.sh --force
```

**Stop specific process:**
```bash
./scripts/stop-mcp.sh --name your-process-name
```

**Manual fallback:**
```bash
pkill -f mcp-test-runner
# or press Ctrl+C in the hung terminal
```

## Obsidian Dataview Troubleshooting

### Dataview Showing Code Instead of Rendering

**Symptom:** Dataview queries display as code blocks instead of executing:
````markdown
```dataview
TABLE status, priority
FROM "_work_efforts_"
```
````

**FIRST SOLUTION (fixes 90% of cases):**
1. **Restart Obsidian completely** (Cmd+Q on Mac, close and reopen)
2. Wait for vault to fully index (watch status bar)
3. Check if dataview now renders

**If restart doesn't work:**
1. Open Settings → Community plugins
2. Verify "Dataview" toggle is ON (enabled)
3. Click gear icon next to Dataview
4. Verify these settings:
   - "Enable Inline Queries" = ON
   - "Enable JavaScript Queries" = ON
   - "Refresh Interval" = 2500ms (default)
5. Close settings and reload note (Cmd+R)

**If still not working:**
1. Check YAML frontmatter format in work effort files:
   ```yaml
   ---
   title: "Work Effort Title"
   status: "active"
   priority: "high"
   ---
   ```
2. Verify files are in correct location (not excluded from indexing)
3. Try simple LIST query first to isolate issue:
   ````markdown
   ```dataview
   LIST
   FROM "_work_efforts_"
   ```
   ````

### Common Dataview Errors

**"No results to show for query"**
- ✅ Correct: Files exist but don't match WHERE clause
- ❌ Check: YAML frontmatter fields match query exactly
- ❌ Check: Folder path is correct (case-sensitive)
- ❌ Check: Files have been indexed (open file once to force index)

**"Dataview: No results to show for list query"**
- Usually means folder/path not found
- Try absolute path from vault root
- Check for typos in folder name
- Verify folder exists in file explorer

### Testing Dataview Installation

Add this query to any note to test if dataview is working:
````markdown
```dataview
LIST
FROM ""
LIMIT 5
```
````

This should show 5 files from your vault. If it shows code, dataview is not running.

### Quick Troubleshooting Checklist

Before debugging complex issues, try these in order:

1. **⚠️ RESTART OBSIDIAN FIRST** ← Fixes most issues
2. Check that required plugins are enabled
3. Verify file/folder paths are correct
4. Check YAML frontmatter format
5. Review error messages in developer console (Cmd+Opt+I)

## Common workflows

### Starting new work
```bash
# Clone the relevant repo
cd /path/to/your/projects
gh repo clone [your-username]/[repo-name]

# Check for uncommitted changes before starting
cd [repo-name]
git status

# Check if _work_efforts_/ system exists
ls -la _work_efforts_/ 2>/dev/null

# Install/update cursor-coding-protocols tooling from central clone
~/Code/cursor-coding-protocols/install.sh --target "$(pwd)"  # adjust path as needed
```

> Maintain a single clone of the toolkit (e.g., `~/Code/cursor-coding-protocols`) and reuse it for every project.

### Regular maintenance
```bash
# Check all git repos for uncommitted changes
for dir in */; do
  cd "$dir"
  if [ -d .git ]; then
    echo "=== $dir ==="
    git status -s
  fi
  cd ..
done

# Push all repos with changes
for dir in */; do
  cd "$dir"
  if [ -d .git ]; then
    echo "=== Pushing $dir ==="
    git add -A
    git commit -m "Backup $(date +%Y-%m-%d)"
    git push
  fi
  cd ..
done
```

### Cleanup operations
```bash
# Find and delete node_modules
find . -name "node_modules" -type d -prune -exec rm -rf {} +

# Find and delete Python virtual environments
find . -name "venv" -type d -prune -exec rm -rf {} +
find . -name ".venv" -type d -prune -exec rm -rf {} +

# Find large files (>100MB)
find . -type f -size +100M 2>/dev/null
```

## Directory structure
```
project-root/
├── .cursor/
│   ├── mcp.json     # MCP server configuration (3 servers)
│   └── rules/       # Cursor-specific AI rules (.mdc files)
├── .mcp-servers/
│   ├── work-efforts/ # Custom work efforts MCP server ⭐
│   └── simple-tools/ # Custom utilities MCP server ⭐
├── .gitignore       # Excludes _work_efforts_/ by default (see below)
├── README.md        # Project documentation
├── AGENTS.md        # This file - AI agent instructions
└── [your-files]/    # Your project files and directories
```

**Note:** `_work_efforts_/` is excluded from git by default via `.gitignore` because work efforts are typically personal task tracking. If you want to track your work efforts in git, simply remove or comment out the `_work_efforts_/` line in `.gitignore`.

**Optional organization patterns:**
```
project-root/
├── src/             # Source code
├── docs/            # Documentation
├── tests/           # Test files
├── _work_efforts_/    # Johnny Decimal work tracking
└── scripts/         # Build and utility scripts
```

## Code style & conventions

### Work Efforts System
Many repos use the `_work_efforts_/` system with Johnny Decimal organization:
- **Structure:** `XX-XX_topic/XX_area/XX.XX_document.md`
- **Categories:** 00-09 (meta), 10-19 (development), 20-29 (features), etc.
- **Index files:** Each subcategory has `00.00_index.md` with links
- **Status folders:** `active/`, `completed/`, `paused/`

**Git Tracking:** By default, `_work_efforts_/` is excluded from git (added to `.gitignore`) since work efforts are personal task tracking. If you want to track your work efforts in version control, remove the `_work_efforts_/` line from `.gitignore`.

**Creating work efforts:**
1. Prefer the MCP work-efforts server so entries inherit existing Johnny Decimal folders
2. Supply `category_name` / `subcategory_name` when introducing brand-new folders
3. Manual creation is still fine—keep numbering consistent and follow `XX-XX_topic` naming
4. Update the subcategory index file after adding a document
5. Update the devlog with progress notes

**Example structure:**
```
_work_efforts_/
├── 00.00_index.md          # VAULT-WIDE INDEX (Obsidian Dataview queries)
├── devlog.md               # Chronological development log
├── 00-09_meta/
│   ├── 00_planning/
│   │   └── 00.01_project-setup.md
│   └── 01_documentation/
├── 10-19_development/
│   ├── 10_backend/
│   └── 11_frontend/
└── 20-29_testing/
```

**CRITICAL INDEX LOCATION:**
- `00.00_index.md` is at **ROOT** of `_work_efforts_/`
- It's a VAULT-WIDE index with Obsidian Dataview queries
- Lists ALL work efforts across all categories
- NOT per-subcategory - that's the OLD way

### Commit messages
- Use clear, descriptive messages
- Format: "Action: description" (e.g., "feat: add user auth")
- Include "Backup [date]" for routine backups
- Reference work effort numbers when applicable

### Git practices
- Commit frequently
- Push at end of work session
- Never commit `node_modules/`, `venv/`, `.env`, or build artifacts
- Use `.gitignore` appropriately

## Testing instructions
```bash
# Check if tests exist in a repo
cd [repo-name]
ls -la | grep -E "test|spec|__tests__"

# Run tests (varies by project)
npm test          # Node.js projects
pnpm test        # pnpm projects
pytest           # Python projects
cargo test       # Rust projects
```

**Before committing:**
1. Run linter if available (`npm run lint`, `eslint`, `ruff`, etc.)
2. Run tests if they exist
3. Check for TypeScript errors (`tsc --noEmit`)

## Cleanup schedules

### Weekly (Every Friday)
- Commit all work in progress
- Push all changes to GitHub
- Delete `node_modules/` in inactive projects
- Remove temporary test files

### Monthly (Last day of month)
- Review all repos for uncommitted changes
- Push all pending commits
- Delete build artifacts (`dist/`, `build/`, `.next/`, etc.)
- Remove unused virtual environments
- Archive completed projects

### Quarterly (End of quarter)
- **Full backup verification:** `gh repo list [your-username] --limit 100`
- **Disk space audit:** `du -sh .`
- Archive projects untouched for 6+ months
- Delete local copies of archived projects

### Annually (December 31st)
- Major cleanup day (like September 30, 2025)
- Full backup of all repos
- Complete deletion of non-essential files
- Fresh start for new year

## Disk space targets

| Status | Disk Usage | Action |
|--------|------------|--------|
| 🟢 Healthy | < 10GB | None |
| 🟡 Monitor | 10-20GB | Review large projects |
| 🟠 Warning | 20-30GB | Monthly cleanup needed |
| 🔴 Critical | > 30GB | **Immediate cleanup required** |

**When disk usage is critical:**
1. Identify largest directories: `du -sh */ | sort -hr | head -10`
2. Check for node_modules: `find . -name "node_modules" -type d`
3. Check for build artifacts: `find . -type d -name "dist" -o -name "build"`
4. Verify backups before deleting
5. Execute systematic cleanup

## Security considerations

### Before cloning repos
- Verify repo ownership: `gh repo view [your-username]/[repo-name]`
- Check for sensitive files in .gitignore
- Never clone unverified third-party repos without review

### Environment variables
- Never commit `.env` files
- Use `.env.example` for templates
- Store secrets in system keychain or password manager

### API keys and tokens
- GitHub CLI is authenticated for this user
- Check auth status: `gh auth status`
- Tokens are stored securely by gh CLI

## User preferences

### Communication style
- Direct and efficient
- Confirm destructive operations explicitly
- Provide summaries with verification steps
- Use structured markdown for clarity

### Work style
- Follows structured work effort system
- Values comprehensive documentation
- Prefers systematic approaches over ad-hoc
- Regular cleanup and maintenance advocate
- Backs up everything before deletion

### File organization
- Uses Johnny Decimal for work efforts
- Prefers clear directory structures
- Documents processes and decisions
- Maintains devlogs for project tracking

## Key files & references

- **GitHub Profile:** Configure in your setup
- **Deletion Manifests:** `~/deletion_manifest_*.txt`
- **This README:** `README.md` (project documentation)
- **AGENTS.md:** This file - AI agent instructions

## Troubleshooting

### "Permission denied" errors
```bash
# Fix permissions on a directory
chmod -R u+w [directory]

# If sudo required, ask user first
echo "This requires sudo. Please run: sudo rm -rf [directory]"
```

### "Repository not found" on GitHub
```bash
# List all repos to verify name
gh repo list [your-username]

# Check if repo is private
gh repo view [your-username]/[repo-name]
```

### Disk space not freeing up
```bash
# Empty trash (macOS)
# Note: Ask user first
echo "Run: rm -rf ~/.Trash/*"

# Check for Docker images/containers
docker system df
```

## Notes for AI agents

1. **Always verify before destroying:** Check GitHub backups before any deletion
2. **Create paper trails:** Generate manifest files for all major operations
3. **Respect the schedules:** Follow cleanup cadence defined above
4. **Update documentation:** Modify README.md and this file after significant changes
5. **Check for _work_efforts_:** Many repos have structured task tracking
6. **User expects confirmation:** For deletions, get explicit "yes" or "delete" confirmation
7. **Systematic over bulk:** Process directories one at a time during cleanup
8. **Document everything:** Update devlogs and work efforts during development
9. **MCP server awareness:** The work-efforts server now preserves Johnny Decimal folders—provide optional names when adding new categories or subcategories.
10. **Manual work efforts:** Always create work efforts manually in the correct Johnny Decimal folders

## Project history

Track your project's major milestones and changes here:

**2025-10-01 - MCP Work-Efforts Server Bug Discovery:**
- Discovered critical bug in work-efforts MCP server
- Server creates generic folder names (`_category`, `_subcategory`) instead of respecting Johnny Decimal structure
- Updated AGENTS.md with warnings in 3 locations
- Created `.cursor/rules/work-efforts-management.mdc` rule file
- Decision: Manual work effort creation only until server is fixed
- Lesson: Automated tools must respect existing structure

**2025-10-03 - Work Efforts Directory Rename:**
- Renamed `_work_efforts` directory to `_work_efforts_` for Obsidian compatibility
- Updated installer scripts, docs, and MCP helpers to reference the new name
- Added regression coverage to ensure agents use the renamed path

**2025-10-03 - MCP Work-Efforts Server Auto-Detection:**
- Implemented directory auto-detection with optional descriptive names
- Updated AGENTS.md and templates to reflect the restored workflow
- Added regression tests for Johnny Decimal folder resolution

**2025-10-02 - Obsidian Integration Re-engineering:**
- Added full YAML frontmatter support to MCP work-efforts server
- Implemented priority, phase, and tags fields for Dataview compatibility
- Added non-destructive editing warnings for Daily Notes
- Created comprehensive Obsidian troubleshooting documentation
- Updated README with Obsidian integration section
- Created docs/OBSIDIAN-INTEGRATION.md with complete guide
- Fixed: Work efforts now fully compatible with Obsidian Dataview plugin

**Example:**
```
**2025-10-01 - Initial Setup:**
- Installed cursor-coding-protocols toolkit
- Configured 3 MCP servers (Filesystem, Work Efforts, Simple Tools)
- Set up Johnny Decimal work efforts system
- Established cleanup schedules

**Next scheduled maintenance:** [Date] (Monthly cleanup)
```

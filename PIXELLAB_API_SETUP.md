# PixelLab API Setup Guide

This guide explains how to securely configure your PixelLab API credentials for the AI-DnD project.

## Getting Your API Key

1. Visit [PixelLab](https://www.pixellab.ai/vibe-coding)
2. Sign up or log in to your account
3. Navigate to your API settings
4. Copy your API key

## Security Best Practices

**⚠️ NEVER commit API keys to version control!**

- API keys are sensitive credentials
- Exposed keys can be used by others, consuming your credits
- Always use environment variables for API keys

## Setup Instructions

### Option 1: Environment Variables (Recommended)

#### Linux/macOS

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export PIXELLAB_API_KEY="your-api-key-here"
```

Then reload your shell:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

For a single session only:

```bash
export PIXELLAB_API_KEY="your-api-key-here"
python pixellab_integration/examples/01_basic_character_generation.py
```

#### Windows (PowerShell)

For current session:

```powershell
$env:PIXELLAB_API_KEY="your-api-key-here"
```

Permanently:

```powershell
[System.Environment]::SetEnvironmentVariable('PIXELLAB_API_KEY', 'your-api-key-here', 'User')
```

#### Windows (Command Prompt)

For current session:

```cmd
set PIXELLAB_API_KEY=your-api-key-here
```

### Option 2: .env File (Local Development)

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:

```
PIXELLAB_API_KEY=your-actual-api-key-here
```

3. The `.env` file is already in `.gitignore` and will NOT be committed

4. Load environment variables before running scripts:

```bash
# Using python-dotenv
pip install python-dotenv

# In your Python script
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: MCP Configuration

For Claude Code MCP integration:

1. Copy the example configuration:

```bash
cp .mcp.json.example .mcp.json
```

2. The `.mcp.json` file uses the `PIXELLAB_API_KEY` environment variable
3. Ensure the environment variable is set (see Option 1)
4. The `.mcp.json` file is in `.gitignore` and will NOT be committed

## Verifying Your Setup

Check if your environment variable is set:

### Linux/macOS

```bash
echo $PIXELLAB_API_KEY
```

### Windows (PowerShell)

```powershell
echo $env:PIXELLAB_API_KEY
```

### Windows (Command Prompt)

```cmd
echo %PIXELLAB_API_KEY%
```

## Testing the Integration

Once your API key is configured, test it:

```bash
cd pixellab_integration
python examples/01_basic_character_generation.py
```

## Troubleshooting

### Error: "PIXELLAB_API_KEY environment variable not set"

**Solution:** Set the environment variable using one of the methods above.

### Error: HTTP 403 Forbidden

**Possible causes:**
- Invalid API key
- Expired API key
- Insufficient credits

**Solution:**
1. Verify your API key is correct
2. Check your account status at https://www.pixellab.ai
3. Ensure you have sufficient credits

### API key not loading from .env file

**Solution:**
1. Make sure python-dotenv is installed: `pip install python-dotenv`
2. Add `load_dotenv()` at the top of your script
3. Verify the `.env` file is in the correct directory

## File Security Checklist

The following files are protected from version control:

- ✅ `.env` - Local environment variables
- ✅ `.env.local` - Local overrides
- ✅ `.mcp.json` - MCP configuration with secrets
- ✅ `*apikey*` - Any file containing "apikey"
- ✅ `*secret*` - Any file containing "secret"
- ✅ `*credentials*` - Any file containing "credentials"

## What Gets Committed

These template files are safe to commit:

- ✅ `.env.example` - Template without actual keys
- ✅ `.mcp.json.example` - Template MCP configuration
- ✅ Example scripts (use environment variables)
- ✅ Documentation files

## Managing Multiple API Keys

If you work with multiple PixelLab accounts:

```bash
# Development account
export PIXELLAB_API_KEY="dev-key-here"
python script.py

# Production account
export PIXELLAB_API_KEY="prod-key-here"
python script.py
```

## CI/CD Integration

For GitHub Actions or other CI/CD:

1. Add `PIXELLAB_API_KEY` as a repository secret
2. Reference it in your workflow:

```yaml
env:
  PIXELLAB_API_KEY: ${{ secrets.PIXELLAB_API_KEY }}
```

## Additional Resources

- [PixelLab Website](https://www.pixellab.ai)
- [PixelLab MCP Setup](https://www.pixellab.ai/vibe-coding)
- [Python dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [Environment Variables Guide](https://en.wikipedia.org/wiki/Environment_variable)

## Support

If you encounter issues:

1. Check your API key is valid at https://www.pixellab.ai
2. Review the troubleshooting section above
3. Join the [PixelLab Discord](https://discord.gg/pBeyTBF8T7)
4. Contact PixelLab support

---

**Remember: Keep your API keys secret! Never share them or commit them to version control.**

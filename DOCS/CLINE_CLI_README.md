# Cline CLI - Installation and Usage Guide

## Overview

Cline CLI is a Python-based command-line interface for AI-powered coding assistance with **Model Context Protocol (MCP) support**. This implementation provides a functional alternative to Node.js-based Cline CLI, especially useful in environments where npm installation faces compatibility issues.

## Installation

### Prerequisites
- Python 3.6 or higher
- `requests` library (install with `pip install requests`)
- Node.js and npm (for MCP servers that require them)

### Setup Instructions

1. **Clone or download cline-cli script:**
   ```bash
   # The script should already be in your project directory
   ls -la cline-cli
   ```

2. **Make the script executable:**
   ```bash
   chmod +x cline-cli
   ```

3. **Create a convenient symlink (optional):**
   ```bash
   cp cline-cli cline
   chmod +x cline
   ```

4. **Install required Python dependencies:**
   ```bash
   pip install requests
   ```

## Usage

### Initial Setup

Configure Cline CLI with your Anthropic API key:

```bash
# Interactive setup (will prompt for API key)
./cline setup

# Or provide API key directly
./cline setup --api-key "your-anthropic-api-key"

# Specify a different model
./cline setup --api-key "your-api-key" --model "claude-3-haiku-20240307"
```

### Chat Interface

Start an interactive chat session:

```bash
./cline chat
```

Send a single message:

```bash
./cline chat "Explain this Python code snippet"
```

### Chat with MCP Tools

Start an interactive chat session with MCP tools enabled:

```bash
./cline chat --mcp
```

Send a single message with MCP context:

```bash
./cline chat --mcp "Search the web for information about..."
```

### File Analysis

Analyze a specific file:

```bash
./cline chat --file path/to/your/file.py
./cline chat --file README.md
```

### File Analysis with MCP

Analyze a file with MCP tools enabled:

```bash
./cline chat --file main.py --mcp
```

### Directory Analysis

Analyze a directory structure:

```bash
./cline chat --directory ./src
./cline chat --directory ./docs
```

### Directory Analysis with MCP

Analyze a directory with MCP tools:

```bash
./cline chat --directory ./src --mcp
```

## Model Context Protocol (MCP) Integration

### MCP Server Management

Cline CLI includes built-in support for popular MCP servers:

#### Available MCP Servers

| Server | Description | Status | Setup Required |
|---------|-------------|--------|----------------|
| **filesystem** | File system access for reading and writing files | Enabled by default | None |
| **brave-search** | Web search using Brave Search API | Disabled by default | Brave API key |
| **github** | GitHub repository access and management | Disabled by default | GitHub token |
| **sqlite** | SQLite database access and querying | Enabled by default | None |
| **weather** | Real-time weather information | Enabled by default | None |
| **linear** | Linear project management integration | Disabled by default | Linear API key |

#### MCP Commands

**Show MCP server status:**
```bash
./cline mcp status
```

**List available MCP tools:**
```bash
./cline mcp list
```

**Enable/Disable MCP servers:**
```bash
# Enable brave-search
./cline mcp setup brave-search --enable

# Disable github
./cline mcp setup github --disable

# Set API key for brave-search
./cline mcp setup brave-search --api-key "your-brave-api-key"

# Set GitHub token
./cline mcp setup github --api-key "your-github-token"
```

#### MCP Configuration Files

- `~/.cline/config.json` - Main Cline CLI configuration
- `~/.cline/mcp_servers.json` - MCP server configurations

### MCP Usage Examples

**Chat with web search:**
```bash
./cline mcp setup brave-search --enable
./cline mcp setup brave-search --api-key "your-api-key"
./cline chat --mcp "Search for latest Python best practices"
```

**Chat with file system access:**
```bash
./cline chat --mcp "List all Python files in the current directory and analyze their structure"
```

**Chat with GitHub integration:**
```bash
./cline mcp setup github --enable
./cline mcp setup github --api-key "your-github-token"
./cline chat --mcp "Show me the latest commits in my repository"
```

## Configuration

### Main Configuration

Cline CLI stores configuration in `~/.cline/config.json`. The configuration includes:

- `api_key`: Your Anthropic API key
- `model`: The AI model to use (default: claude-3-sonnet-20240229)
- `endpoint`: API endpoint URL

### MCP Configuration

MCP server configurations are stored in `~/.cline/mcp_servers.json`. Each server includes:

- `command`: The command to run the MCP server
- `args`: Command arguments
- `description`: Server description
- `enabled`: Whether the server is enabled
- `env`: Environment variables (for servers requiring API keys)

## Features

### Core Features
- 🤖 **AI-powered coding assistance** via Anthropic Claude models
- 📁 **File analysis** with syntax highlighting
- 📂 **Directory structure analysis**
- 💬 **Interactive chat mode**
- ⚙️ **Easy configuration** management

### MCP-Enhanced Features
- 🔧 **File system access** for reading and writing files
- 🔍 **Web search** via Brave Search API
- 🐙 **GitHub integration** for repository management
- 🗄️ **Database access** via SQLite
- 🌤️ **Weather information** from real-time sources
- 📋 **Project management** via Linear integration
- 🔌 **Extensible architecture** for adding new MCP servers

### Interactive Chat Commands
When in interactive mode, you can use:
- `help` - Show available commands
- `clear` - Clear the screen
- `exit` or `quit` - Exit the chat session
- Type any message to get AI assistance

### Supported File Types
The directory analysis recognizes:
- Python files (`.py`)
- JavaScript files (`.js`)
- TypeScript files (`.ts`)
- Markdown files (`.md`)
- Text files (`.txt`)
- JSON files (`.json`)
- YAML files (`.yaml`, `.yml`)

## Examples

### Basic Usage
```bash
# Setup
./cline setup

# Chat with file analysis
./cline chat --file main.py

# Directory analysis
./cline chat --directory ./src
```

### MCP-Enhanced Usage
```bash
# Enable web search
./cline mcp setup brave-search --enable
./cline mcp setup brave-search --api-key "your-brave-api-key"

# Chat with web search
./cline chat --mcp "What are the latest developments in AI?"

# Enable GitHub integration
./cline mcp setup github --enable
./cline mcp setup github --api-key "your-github-token"

# Chat with GitHub access
./cline chat --mcp "Show me my recent GitHub activity"

# File analysis with MCP
./cline chat --file README.md --mcp
```

### Advanced Workflows

**Development workflow with MCP:**
```bash
# 1. Setup all required MCP servers
./cline mcp setup filesystem --enable  # Already enabled
./cline mcp setup sqlite --enable       # Already enabled
./cline mcp setup brave-search --enable
./cline mcp setup brave-search --api-key "your-api-key"

# 2. Start enhanced chat session
./cline chat --mcp

# Now you can:
# - Read/write files using filesystem MCP
# - Search the web using brave-search MCP
# - Query databases using sqlite MCP
# - Get weather information using weather MCP
```

**Project analysis workflow:**
```bash
# Analyze entire project with MCP tools
./cline chat --directory ./src --mcp "Analyze this codebase and suggest improvements"

# Get weather for deployment planning
./cline chat --mcp "What's the weather forecast for the next week?"
```

## Troubleshooting

### API Key Issues
If you get an API key error:
1. Run `./cline setup` again to reconfigure
2. Verify your API key is valid and active
3. Check your Anthropic account billing status

### MCP Server Issues
If MCP servers don't work:
1. Check Node.js and npm are installed: `node --version` and `npm --version`
2. Verify MCP server status: `./cline mcp status`
3. Check API keys: `./cline mcp status` (masked keys shown)
4. Test individual servers: `./cline mcp list`

### Permission Errors
If you get permission denied:
```bash
chmod +x cline-cli
chmod +x cline
```

### Missing Dependencies
If you get import errors:
```bash
pip install requests
```

### MCP Server Installation Issues
If MCP servers fail to start:
1. Ensure npm is installed and accessible
2. Check internet connectivity for npm package downloads
3. Verify firewall settings don't block npm
4. Try manual installation: `npx @modelcontextprotocol/server-filesystem`

## API Model Options

- `claude-3-sonnet-20240229` (default) - Balanced performance and speed
- `claude-3-haiku-20240307` - Fastest response
- `claude-3-opus-20240229` - Highest quality, slower

## Security Notes

- Your API key is stored locally in `~/.cline/config.json`
- MCP API keys are stored in `~/.cline/mcp_servers.json`
- Ensure proper file permissions on your config directory
- Never share your API keys or commit them to version control
- Consider using environment variables for API keys in production
- MCP servers run with the same permissions as your user account

## Comparison with Node.js Version

This Python implementation provides:
- ✅ Same core functionality as the original Cline CLI
- ✅ **Full MCP support** with multiple pre-configured servers
- ✅ Better compatibility in mixed OS environments
- ✅ No Node.js/npm dependencies for the CLI itself
- ✅ Lightweight and fast startup
- ✅ Extensible MCP architecture
- ⚠️ Some advanced features may differ from the original

## Getting Help

For issues with this implementation:
1. Check this README first
2. Verify your Python and requests installation
3. Ensure your API key is valid
4. Test MCP server status: `./cline mcp status`
5. Test with a simple message first

For API-related issues, visit [Anthropic documentation](https://docs.anthropic.com/).

For MCP-related issues, visit the specific MCP server documentation or check the [Model Context Protocol specification](https://modelcontextprotocol.io/).

## Version Information

Current version: `2.0.0 with MCP support`

Check your version:
```bash
./cline --version

# TodoWatch

A lightweight GUI application that monitors your codebase for TODO and FIXME comments in real-time.

## Features

- 🔍 **Real-time Monitoring** - Automatically detects file changes and updates the task list
- 📝 **TODO & FIXME Tracking** - Scans your entire project for TODO and FIXME comments
- 🎨 **Color-coded Display** - TODOs in blue, FIXMEs in red for easy distinction
- 🚫 **Customizable Ignore List** - Skip directories like `node_modules`, `.git`, etc.
- 📋 **Quick Copy** - Double-click any item to copy the file path and line number
- ⚡ **Fast Scanning** - Powered by ripgrep for lightning-fast searches

## Screenshots

![TodoWatch Interface](screenshot.png)

## Requirements

- Python 3.6+
- [ripgrep](https://github.com/BurntSushi/ripgrep) (rg command)

## Installation

### 1. Install ripgrep

**macOS:**

```bash
brew install ripgrep
```

**Ubuntu/Debian:**

```bash
apt install ripgrep
```

**Windows:**

```bash
choco install ripgrep
```

Or download from [ripgrep releases](https://github.com/BurntSushi/ripgrep/releases)

### 2. Clone and Run

```bash
git clone https://github.com/yourusername/todowatch.git
cd todowatch
python todowatch.py
```

No additional Python dependencies required - uses only standard library!

## Usage

1. **Select Directory** - Click "Browse" and choose your project directory
2. **Start Monitoring** - Click "Start Monitoring" to enable real-time file watching
3. **View Tasks** - All TODO and FIXME comments appear in the list with file location and line number
4. **Copy Location** - Double-click any task to copy its file path and line number to clipboard
5. **Customize Ignores** - Click "Ignore List" to add or remove ignored directories

### Default Ignored Directories

- `node_modules`
- `.git`
- `__pycache__`
- `.venv` / `venv`
- `dist` / `build`
- `.next` / `.nuxt`
- `target`
- `vendor`

## How It Works

TodoWatch uses ripgrep to efficiently search for TODO and FIXME patterns in your codebase. It monitors file modification timestamps and automatically rescans when changes are detected (checks every 2 seconds).

The application recognizes these comment patterns:

- `TODO:`
- `FIXME:`

## Tips

- Use the manual "Refresh" button to force an immediate scan
- Add custom patterns to the ignore list for project-specific directories
- The status bar shows the current state and total number of tasks found
- Monitoring continues in the background while you work

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

MIT License - feel free to use this in your projects!

## Acknowledgments

- Built with Python's tkinter for the GUI
- Powered by [ripgrep](https://github.com/BurntSushi/ripgrep) for blazing-fast text search

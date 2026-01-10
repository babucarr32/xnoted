# XNoted

A terminal-based todo, notes and project management application built with Python and Textual.

## Features

- **Notes Management**: Organize notes into projects
- **Project Management**: Organize todos into projects
- **Task Management**: Create, update, and track todos within projects
- **Terminal UI**: Modern, keyboard-driven interface powered by Textual
- **SQLite Database**: Persistent storage for projects and tasks
- **Keyboard Shortcuts**: Fast navigation and task creation

## Requirements

- Python >= 3.11
- Dependencies:
  - textual >= 6.6.0
  - textual-dev >= 1.8.0

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd xnoted
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Usage

Activate the virtual environment
### On macOS/Linux (Bash/Zsh):
```bash
source .venv/bin/activate
```

### On Windows:

**Command Prompt (CMD):**
```cmd
.venv\Scripts\activate.bat
```
Run the application:
```bash
textual run --dev main.py
```

### Keyboard Shortcuts

- `Ctrl+N` - Create new todo/note
- `Ctrl+L` - Select project
- `Ctrl+B` - Create new project
- `Ctrl+D` - Scroll body down
- `Ctrl+U` - Scroll body up

## Project Structure

```
xnoted/
├── app.py                 # Main application class
├── main.py               # Entry point
├── database.db           # SQLite database
├── src/
│   ├── components/       # UI components
│   ├── screens/          # Modal screens
│   ├── styles/           # Textual CSS styles
│   └── utils/            # Database and utility functions
└── pyproject.toml        # Project configuration
```

## Development

The application uses Textual for the terminal UI. Key components:

- **XNotedApp**: Main application class with keyboard bindings
- **Database**: SQLite wrapper for data persistence
- **Screens**: Modal dialogs for creating todos and projects
- **Components**: Reusable UI elements

## License

MIT

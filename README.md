# Auto Clicker

A simple, lightweight auto clicker with a graphical interface. Built as a learning project for Python programming concepts.

## Features

- **Adjustable Click Speed** - Set clicks per second (1-50 CPS)
- **Hotkey Toggle** - Press F6 to start/stop (works even when window is not focused)
- **Mouse Button Selection** - Choose left or right click
- **Click Counter** - Track total clicks
- **Portable** - Single .exe file, no installation required

## Download

Download the latest release from the [Releases](../../releases) page.

## Usage

1. Download `AutoClicker.exe` from Releases
2. Run the application
3. Adjust clicks per second using the slider
4. Select left or right mouse button
5. Press **F6** or click **Start** to begin auto clicking
6. Press **F6** or click **Stop** to stop

## Build from Source

### Requirements
- Python 3.11+
- pip

### Steps

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/auto-clicker.git
cd auto-clicker

# Install dependencies
pip install -r requirements.txt

# Run directly
python src/auto_clicker.py

# Build executable
pyinstaller --onefile --windowed --name AutoClicker src/auto_clicker.py
```

The executable will be in the `dist/` folder.

## Learning Topics

This project demonstrates:
- **Python Basics** - Variables, functions, classes
- **GUI Programming** - Tkinter widgets and layouts
- **Threading** - Background tasks without freezing UI
- **Event Handling** - Button clicks, keyboard hotkeys
- **Packaging** - Creating standalone executables

## License

MIT License - see [LICENSE](LICENSE) file.

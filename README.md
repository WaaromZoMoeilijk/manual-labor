# Manual Labor

A feature-rich auto clicker with a graphical interface. Built as a learning project for Python programming concepts.

*Because clicking is hard work.*

## Features

### Speed Control
- **Adjustable CPS** - Set clicks per second (1-50)
- **Timing Variation** - Add ±0-30% random variation to click timing

### Click Options
- **Mouse Button Selection** - Left, right, or middle click
- **Double Click Mode** - Perform double clicks
- **Click Limit** - Auto-stop after X clicks (0 = unlimited)
- **Fixed Position** - Click at specific X,Y coordinates with capture button

### Controls
- **Custom Hotkey** - Choose F6, F7, F8, F9, or F10
- **Hold Mode** - Click only while holding the hotkey
- **Start Delay** - Countdown before clicking starts

### Extras
- **Click Sound** - Audio feedback on each click
- **Dark Mode** - Easy on the eyes
- **Save/Load Settings** - Preferences persist between sessions
- **Click Counter** - Track total clicks
- **Portable** - Single .exe file, no installation required

## Download

Download the latest release from the [Releases](../../releases) page.

## Usage

1. Download `ManualLabor.exe` from Releases
2. Run the application
3. Configure your settings:
   - Adjust CPS and timing variation
   - Select mouse button and click mode
   - Set position, hotkey, and other options
4. Press your hotkey (default: **F6**) or click **Start**
5. Press hotkey again or click **Stop** to stop

## Build from Source

### Requirements
- Python 3.11+
- pip

### Steps

```bash
# Clone the repository
git clone https://github.com/WaaromZoMoeilijk/manual-labor.git
cd manual-labor

# Install dependencies
pip install -r requirements.txt

# Run directly
python src/manual_labor.py

# Run tests
pytest tests/ -v

# Build executable
pyinstaller --onefile --windowed --name ManualLabor src/manual_labor.py
```

The executable will be in the `dist/` folder.

## Learning Topics

This project demonstrates:
- **Python Basics** - Variables, functions, classes
- **GUI Programming** - Tkinter widgets, layouts, theming
- **Threading** - Background tasks without freezing UI
- **Event Handling** - Button clicks, keyboard hotkeys
- **File I/O** - JSON settings persistence
- **Packaging** - Creating standalone executables
- **CI/CD** - GitHub Actions for automated builds

## License

MIT License - see [LICENSE](LICENSE) file.

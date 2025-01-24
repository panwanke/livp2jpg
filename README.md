# [Livp2jpg Converter](https://github.com/panwanke/livp2jpg.git)

This tool can convert .livp files to .jpg files easily. It provides both command line and GUI versions.

## Installation

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the GUI version directly:
    ```bash
    python converter_gui.py
    ```

3. (Optional) Build executable:
    ```bash
    pyinstaller --onefile --noconsole converter_gui.py
    ```

## Usage

### GUI Version
1. Run the executable:
    ```bash
    dist/converter_gui.exe
    ```
2. Select .livp files
3. Click "Convert" button


## Notes
- The GUI version is recommended for most users
- Both versions support batch processing of multiple .livp files

# Modular Application

A modular application with separate features, each in its own file. Available with both command-line and graphical user interfaces.

## Features

### 1. Image Compressor
Compresses images to a specified target file size while maintaining as much quality as possible.

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/modular-app.git
cd modular-app
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### Command-Line Interface

#### Image Compressor

Compress an image to a specific file size (in kilobytes):

```
python main.py compress input_image.jpg output_image.jpg --size 200
```

This will compress `input_image.jpg` to approximately 200KB and save it as `output_image.jpg`.

### Graphical User Interface

Run the GUI version of the application:

```
python gui_main.py
```

The GUI provides an easy-to-use interface for all features:
1. Select the feature tab you want to use
2. Fill in the required information 
3. Click the action button to perform the task

## Structure

```
modular-app/
├── main.py                  # Command-line interface entry point
├── gui_main.py              # GUI entry point
├── features/                # Directory containing feature modules
│   ├── __init__.py          # Makes features a proper package
│   ├── image_compressor.py  # Image compression module
│   └── ...                  # Other feature modules
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

## Adding New Features

To add a new feature:

1. Create a new Python file in the `features` directory
2. Import and add the feature to both `main.py` (CLI) and `gui_main.py` (GUI)
3. For the GUI, create a new tab method in the `ModularAppGUI` class
4. Update this README with usage instructions

### Adding a New Tab to the GUI

```python
def create_your_feature_tab(self):
    """Create a new feature tab."""
    tab = ttk.Frame(self.notebook)
    self.notebook.add(tab, text="Your Feature Name")
    
    # Add your GUI elements to the tab
    # ...
    
    # Add action buttons
    button_frame = ttk.Frame(tab)
    button_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Button(button_frame, text="Action", command=self.your_feature_action).pack(side=tk.RIGHT)
```

## License

[MIT License](LICENSE)

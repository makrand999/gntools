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

### Graphical User Interface

Run the GUI version of the application:

```
python gui_main.py
```

The GUI provides an easy-to-use interface for all features:
1. Select the feature tab you want to use
2. Fill in the required information 
3. Click the action button to perform the task

[![Watch the video](https://img.youtube.com/vi/yu5G9p_GwUY/0.jpg)](https://youtu.be/yu5G9p_GwUY)



## Structure

```
modular-app/
├── main.py                  # GUI entry point
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
2. For the GUI, create a new tab method in the `ModularAppGUI` class
3. Update this README with usage instructions

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

<<<<<<< HEAD
[MIT License](LICENSE)
=======
[MIT License](LICENSE)
>>>>>>> 07fbb891f7e2b9a1ce7c32c1c6eaf0428f3795d6

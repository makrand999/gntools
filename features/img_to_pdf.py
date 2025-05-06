#!/usr/bin/env python3
"""
Image to PDF Converter Module
This feature allows converting multiple images to a single PDF with custom ordering.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PIL import Image, ImageTk
import tempfile

class DraggableImageItem(tk.Canvas):
    """Canvas widget that displays an image with a label and supports drag-and-drop reordering."""
    def __init__(self, parent, image_path, width=100, height=100, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.image_path = image_path
        self.parent = parent
        self.width = width
        self.height = height
        
        # Load and resize the image for preview
        self.load_image()
        
        # Draw the image and filename
        self.create_image(width//2, height//2, image=self.tk_img)
        filename = os.path.basename(image_path)
        if len(filename) > 15:
            filename = filename[:12] + "..."
        self.create_text(width//2, height-10, text=filename, fill="black", font=("Arial", 8))
        
        # Configure the canvas for dragging
        self.configure(highlightthickness=1, highlightbackground="gray")
        
        # Bind events for drag and drop
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        # Store drag data
        self.drag_data = {"x": 0, "y": 0, "item": None, "index": -1}
        
    def load_image(self):
        """Load and resize the image for the preview thumbnail."""
        try:
            img = Image.open(self.image_path)
            img.thumbnail((self.width-10, self.height-20))
            self.tk_img = ImageTk.PhotoImage(img)
        except Exception as e:
            # Use a placeholder if image loading fails
            self.tk_img = None
            print(f"Error loading image {self.image_path}: {e}")
            
    def on_press(self, event):
        """Begin drag operation."""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["item"] = self
        # Raise this canvas above others
        self.lift()
        # Change appearance to indicate dragging
        self.configure(highlightbackground="blue", highlightthickness=2)
        
    def on_drag(self, event):
        """Handle drag motion."""
        # Calculate the new position
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Move the canvas
        self.place(x=self.winfo_x() + dx, y=self.winfo_y() + dy)
        
    def on_release(self, event):
        """End drag operation and reorder items."""
        # Reset appearance
        self.configure(highlightbackground="gray", highlightthickness=1)
        
        # Notify parent about the drop for reordering
        if hasattr(self.parent, "reorder_images"):
            self.parent.reorder_images(self)


class ImageToPdfFeature:
    """Image to PDF Converter Feature Class"""
    
    def __init__(self, parent_notebook, status_var):
        """Initialize the Image to PDF feature tab."""
        self.parent_notebook = parent_notebook
        self.status_var = status_var
        self.pdf_image_paths = []
        self.image_items = []
        
        # Create the tab
        self.create_tab()
    
    def create_tab(self):
        """Create the Image to PDF converter tab with its GUI elements."""
        self.tab = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(self.tab, text="Image to PDF")
        
        # Top frame for buttons
        top_frame = ttk.Frame(self.tab)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            top_frame, 
            text="Add Images", 
            command=self.browse_pdf_images
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            top_frame, 
            text="Clear All", 
            command=self.clear_pdf_images
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Instructions
        ttk.Label(
            top_frame, 
            text="Drag to reorder • Double-click to remove", 
            font=("Arial", 9, "italic")
        ).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Create a frame with a scrollbar for the images
        self.image_list_frame = ttk.LabelFrame(self.tab, text="Images (Drag to Reorder)")
        self.image_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.image_list_frame)
        scrollbar = ttk.Scrollbar(self.image_list_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill='y')
        self.canvas.pack(side=tk.LEFT, fill='both', expand=True)
        
        # Frame inside canvas for image thumbnails
        self.images_container = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.images_container, anchor='nw')
        
        # Configure the canvas to resize with the window
        self.images_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Progress bar
        pdf_progress_frame = ttk.LabelFrame(self.tab, text="Progress")
        pdf_progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.pdf_progress_var = tk.DoubleVar()
        self.pdf_progress_bar = ttk.Progressbar(pdf_progress_frame, variable=self.pdf_progress_var, maximum=100)
        self.pdf_progress_bar.pack(fill='x', padx=5, pady=5)
        
        # Action buttons
        pdf_button_frame = ttk.Frame(self.tab)
        pdf_button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            pdf_button_frame, 
            text="Create PDF", 
            command=self.create_pdf_task
        ).pack(side=tk.RIGHT, padx=5, pady=5)
    
    def browse_pdf_images(self):
        """Open a file dialog to select multiple images for PDF creation."""
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        )
        filenames = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        
        if filenames:
            for filepath in filenames:
                if filepath not in self.pdf_image_paths:
                    self.pdf_image_paths.append(filepath)
            
            # Update the UI with the new images
            self.update_image_list()
    
    def update_image_list(self):
        """Update the image list display with current images."""
        # Clear existing items
        for widget in self.images_container.winfo_children():
            widget.destroy()
        
        self.image_items = []
        
        # Create a grid of image items
        if self.pdf_image_paths:
            cols = 4  # Number of columns in the grid
            for i, path in enumerate(self.pdf_image_paths):
                row, col = divmod(i, cols)
                
                # Create the draggable image item
                item = DraggableImageItem(
                    self.images_container, 
                    path, 
                    width=120, 
                    height=120,
                    bg="white",
                )
                item.grid(row=row, column=col, padx=5, pady=5)
                
                # Store reference to the item
                self.image_items.append(item)
                
                # Bind double-click to remove
                item.bind("<Double-Button-1>", lambda e, idx=i: self.remove_image(idx))
        else:
            # Show a message when no images are added
            ttk.Label(
                self.images_container,
                text="No images added yet. Click 'Add Images' to begin.",
                font=("Arial", 10),
                foreground="gray"
            ).grid(row=0, column=0, padx=20, pady=40)
    
    def remove_image(self, index):
        """Remove an image from the list."""
        if 0 <= index < len(self.pdf_image_paths):
            del self.pdf_image_paths[index]
            self.update_image_list()
    
    def reorder_images(self, dropped_item):
        """Handle reordering of images after drag and drop."""
        # Find the grid position where the item was dropped
        x, y = dropped_item.winfo_x() + dropped_item.winfo_width() // 2, dropped_item.winfo_y() + dropped_item.winfo_height() // 2
        
        # Find the closest item at the drop position
        closest_idx = -1
        min_dist = float('inf')
        
        for i, item in enumerate(self.image_items):
            item_x = item.winfo_x() + item.winfo_width() // 2
            item_y = item.winfo_y() + item.winfo_height() // 2
            dist = (x - item_x) ** 2 + (y - item_y) ** 2
            
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
        
        # Find the original index of the dragged item
        orig_idx = -1
        for i, item in enumerate(self.image_items):
            if item == dropped_item:
                orig_idx = i
                break
        
        if orig_idx != -1 and closest_idx != -1 and orig_idx != closest_idx:
            # Reorder the paths list
            img_path = self.pdf_image_paths.pop(orig_idx)
            self.pdf_image_paths.insert(closest_idx, img_path)
            # Update the UI
            self.update_image_list()
    
    def clear_pdf_images(self):
        """Clear all images from the PDF creation list."""
        self.pdf_image_paths = []
        self.update_image_list()
    
    def create_pdf_task(self):
        """Start the PDF creation task in a separate thread."""
        # Validate we have images
        if not self.pdf_image_paths:
            messagebox.showerror("No Images", "Please add at least one image to create a PDF.")
            return
        
        # Ask user where to save the PDF
        output_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        
        if not output_path:
            return  # User cancelled
        
        # Make sure it has .pdf extension
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'
        
        # Start PDF creation in a thread
        self.status_var.set("Creating PDF...")
        self.pdf_progress_var.set(10)  # Show initial progress
        
        thread = threading.Thread(
            target=self._run_pdf_creation,
            args=(self.pdf_image_paths, output_path)
        )
        thread.daemon = True
        thread.start()
    
    def _run_pdf_creation(self, image_paths, output_path):
        """Run the PDF creation task in a separate thread."""
        try:
            # Create the progress callback
            def progress_callback(value):
                self.pdf_progress_var.set(value)
            
            # Create the PDF
            images_to_pdf(image_paths, output_path, progress_callback)
            
            # Schedule UI updates to run on the main thread
            self.tab.after(0, self._pdf_creation_done, output_path)
            
        except Exception as e:
            # Schedule error handling to run on the main thread
            self.tab.after(0, self._pdf_creation_error, str(e))
    
    def _pdf_creation_done(self, output_path):
        """Handle completion of the PDF creation task."""
        self.status_var.set(f"PDF created successfully: {os.path.basename(output_path)}")
        self.pdf_progress_var.set(100)
        
        # Show success message
        messagebox.showinfo(
            "Success", 
            f"PDF created successfully.\nSaved to: {output_path}"
        )
    
    def _pdf_creation_error(self, error_message):
        """Handle errors during PDF creation."""
        self.status_var.set("Error creating PDF")
        self.pdf_progress_var.set(0)
        messagebox.showerror("PDF Creation Error", f"An error occurred:\n{error_message}")


def images_to_pdf(image_paths, output_path, progress_callback=None):
    """
    Convert multiple images to a single PDF with the specified order.
    
    Args:
        image_paths (list): List of paths to images in the desired order
        output_path (str): Path where to save the final PDF
        progress_callback (callable, optional): Function to call with progress updates (0-100)
        
    Returns:
        bool: True on success, False on failure
    """
    try:
        if not image_paths:
            raise ValueError("No images provided")
            
        # Open all images
        images = []
        for i, path in enumerate(image_paths):
            try:
                # Open the image and convert to RGB (required for PDF compatibility)
                img = Image.open(path)
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)
                
                # Report progress for loading images (0-50%)
                if progress_callback:
                    progress = int(50 * (i + 1) / len(image_paths))
                    progress_callback(progress)
                    
            except Exception as e:
                raise ValueError(f"Failed to process image {os.path.basename(path)}: {str(e)}")
        
        if not images:
            raise ValueError("No valid images to convert")
            
        # Get first image
        first_image = images[0]
        
        # Use a temporary file for conversion
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            temp_path = tmp_file.name
            
        # Save remaining images as PDF
        if len(images) > 1:
            first_image.save(
                temp_path,
                save_all=True,
                append_images=images[1:],
                format="PDF"
            )
        else:
            first_image.save(temp_path, format="PDF")
            
        # Report progress for PDF creation (50-90%)
        if progress_callback:
            progress_callback(90)
            
        # Move the temp file to the output path
        import shutil
        shutil.move(temp_path, output_path)
        
        # Report completion
        if progress_callback:
            progress_callback(100)
            
        # Close all images
        for img in images:
            img.close()
            
        return True
        
    except Exception as e:
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        
        # Re-raise the exception
        raise Exception(f"Failed to create PDF: {str(e)}")




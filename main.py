#!/usr/bin/env python3
"""
Modular Application - GUI Entry Point
This module serves as the GUI entry point for the modular application.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# Import feature modules
from features.image_compressor import compress_image

class ModularAppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.title("Modular Application")
        self.geometry("700x500")
        self.resizable(True, True)
        
        # Create a notebook for different features
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add Image Compressor tab
        self.create_image_compressor_tab()
        
        # Add more feature tabs here as needed
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create the features directory if it doesn't exist
        os.makedirs("features", exist_ok=True)
    
    def create_image_compressor_tab(self):
        """Create the image compressor tab with its GUI elements."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Image Compressor")
        
        # Input file section
        input_frame = ttk.LabelFrame(tab, text="Input Image")
        input_frame.pack(fill='x', padx=10, pady=10, anchor='n')
        
        self.input_path_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path_var, width=50).pack(side=tk.LEFT, padx=5, pady=10)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input_file).pack(side=tk.LEFT, padx=5, pady=10)
        
        # Target size section
        size_frame = ttk.LabelFrame(tab, text="Compression Settings")
        size_frame.pack(fill='x', padx=10, pady=10, anchor='n')
        
        ttk.Label(size_frame, text="Target Size (KB):").pack(side=tk.LEFT, padx=5, pady=10)
        self.target_size_var = tk.StringVar(value="200")
        ttk.Entry(size_frame, textvariable=self.target_size_var, width=10).pack(side=tk.LEFT, padx=5, pady=10)
        
        # Progress bar
        progress_frame = ttk.LabelFrame(tab, text="Progress")
        progress_frame.pack(fill='x', padx=10, pady=10, anchor='n')
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Compress Image", 
            command=self.compress_image_task
        ).pack(side=tk.RIGHT, padx=5, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_compression_fields
        ).pack(side=tk.RIGHT, padx=5, pady=10)
    
    def browse_input_file(self):
        """Open a file dialog to select an input image."""
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        )
        filename = filedialog.askopenfilename(title="Select Input Image", filetypes=filetypes)
        if filename:
            self.input_path_var.set(filename)
    
    def clear_compression_fields(self):
        """Clear all fields in the compression tab."""
        self.input_path_var.set("")
        self.target_size_var.set("200")
        self.progress_var.set(0)
        self.status_var.set("Ready")
    
    def compress_image_task(self):
        """Start the image compression task in a separate thread."""
        # Validate inputs
        input_path = self.input_path_var.get()
        
        try:
            target_size = int(self.target_size_var.get())
            if target_size <= 0:
                raise ValueError("Target size must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter a valid target size: {str(e)}")
            return
        
        if not input_path:
            messagebox.showerror("Missing Input", "Please select an input image")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("File Not Found", f"Input file does not exist: {input_path}")
            return
            
        # Create a temporary file for the compressed image
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        temp_output_path = os.path.join(os.path.dirname(input_path), f"temp_{name}_compressed{ext}")
        
        # Start compression in a separate thread to keep the UI responsive
        self.status_var.set("Compressing image...")
        self.progress_var.set(20)  # Show some initial progress
        
        # Create and start the thread
        thread = threading.Thread(
            target=self._run_compression,
            args=(input_path, temp_output_path, target_size)
        )
        thread.daemon = True
        thread.start()
    
    def _run_compression(self, input_path, temp_output_path, target_size):
        """Run the compression task and update the UI when done."""
        try:
            self.progress_var.set(40)
            result = compress_image(input_path, temp_output_path, target_size * 1024)  # Convert KB to bytes
            self.progress_var.set(100)
            
            # Schedule UI updates to run on the main thread
            self.after(0, self._compression_done, result, temp_output_path)
        except Exception as e:
            # Schedule error handling to run on the main thread
            self.after(0, self._compression_error, str(e))
            # Try to clean up temp file if it exists
            try:
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
            except:
                pass
    
    def _compression_done(self, success, temp_output_path):
        """Handle completion of the compression task."""
        try:
            if success:
                final_size_kb = os.path.getsize(temp_output_path) // 1024
                self.status_var.set("Compression complete. Select where to save.")
                
                # Let the user choose where to save the compressed file
                filetypes = (
                    ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                    ("All files", "*.*")
                )
                
                # Get initial filename suggestion
                base_name = os.path.basename(temp_output_path)
                name = os.path.splitext(base_name)[0].replace("temp_", "")
                ext = os.path.splitext(self.input_path_var.get())[1]
                initial_filename = f"{name}{ext}"
                
                output_path = filedialog.asksaveasfilename(
                    title="Save Compressed Image As",
                    filetypes=filetypes,
                    initialfile=initial_filename
                )
                
                if output_path:
                    # Copy the temp file to the chosen location
                    import shutil
                    shutil.copy2(temp_output_path, output_path)
                    
                    # Show success message
                    self.status_var.set(f"Saved. Final size: {final_size_kb} KB")
                    messagebox.showinfo(
                        "Success", 
                        f"Image compressed successfully.\nFinal size: {final_size_kb} KB\nSaved to: {output_path}"
                    )
                else:
                    self.status_var.set("Save cancelled")
            else:
                self.status_var.set("Compression completed but target size not reached")
                messagebox.showwarning(
                    "Warning", 
                    "Compression completed but could not reach the target size while maintaining acceptable quality."
                )
        finally:
            # Clean up the temp file
            try:
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
            except Exception as e:
                print(f"Failed to remove temporary file: {e}")
    
    def _compression_error(self, error_message):
        """Handle errors during compression."""
        self.status_var.set("Error during compression")
        self.progress_var.set(0)
        messagebox.showerror("Compression Error", f"An error occurred during compression:\n{error_message}")


def main():
    # Create and start the GUI
    app = ModularAppGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
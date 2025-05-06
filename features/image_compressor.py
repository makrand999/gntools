#!/usr/bin/env python3
"""
Image Compressor Module
This module provides functionality to compress images to a specified target size.
"""

import os
from PIL import Image
import io

def compress_image(input_path, output_path, target_size_bytes):
    """
    Compress an image to approximately the specified target size.
    
    Args:
        input_path (str): Path to the input image file
        output_path (str): Path where the compressed image will be saved
        target_size_bytes (int): Target file size in bytes
    
    Returns:
        bool: True if compression was successful, False otherwise
    """
    # Open the original image
    original_image = Image.open(input_path)
    
    # Get original format (or default to JPEG)
    img_format = original_image.format if original_image.format else 'JPEG'
    
    # Start with quality 95
    quality = 95
    output_size = float('inf')
    
    # Binary search approach to find the right quality
    min_quality = 5  # Minimum acceptable quality
    max_quality = 95
    
    # Convert PNG to RGB if needed (to avoid errors with palette images)
    if img_format == 'PNG' and original_image.mode == 'RGBA':
        # Create a white background
        background = Image.new('RGBA', original_image.size, (255, 255, 255))
        # Paste the image on the background
        composite = Image.alpha_composite(background, original_image)
        original_image = composite.convert('RGB')
    elif original_image.mode != 'RGB':
        original_image = original_image.convert('RGB')
    
    # Initial compression attempt
    buffer = io.BytesIO()
    original_image.save(buffer, format=img_format, quality=quality, optimize=True)
    output_size = buffer.tell()
    
    # If the image is already smaller than target size, no need to compress
    if output_size <= target_size_bytes:
        original_image.save(output_path, format=img_format, quality=quality, optimize=True)
        return True
    
    # Binary search to find optimal quality
    while min_quality <= max_quality:
        quality = (min_quality + max_quality) // 2
        buffer = io.BytesIO()
        original_image.save(buffer, format=img_format, quality=quality, optimize=True)
        output_size = buffer.tell()
        
        # Check if we're close enough to the target size
        if abs(output_size - target_size_bytes) < target_size_bytes * 0.05:  # Within 5% of target
            break
        
        if output_size > target_size_bytes:
            max_quality = quality - 1
        else:
            min_quality = quality + 1
    
    # If we're still too large, try reducing dimensions
    if output_size > target_size_bytes:
        width, height = original_image.size
        ratio = (target_size_bytes / output_size) ** 0.5  # Square root to apply to both dimensions
        
        # Reduce size iteratively
        while output_size > target_size_bytes and width > 50 and height > 50:
            width = int(width * 0.9)  # Reduce by 10% each time
            height = int(height * 0.9)
            resized_img = original_image.resize((width, height), Image.LANCZOS)
            
            buffer = io.BytesIO()
            resized_img.save(buffer, format=img_format, quality=quality, optimize=True)
            output_size = buffer.tell()
            
            if output_size <= target_size_bytes:
                original_image = resized_img
                break
    
    # Save the final compressed image
    original_image.save(output_path, format=img_format, quality=quality, optimize=True)
    
    # Verify final size
    final_size = os.path.getsize(output_path)
    return abs(final_size - target_size_bytes) < target_size_bytes * 0.2  # Within 20% of target

# Example usage if run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python image_compressor.py input_image output_image target_size_in_kb")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    target_size = int(sys.argv[3]) * 1024  # Convert KB to bytes
    
    result = compress_image(input_file, output_file, target_size)
    print(f"Compression {'successful' if result else 'could not reach target size'}")
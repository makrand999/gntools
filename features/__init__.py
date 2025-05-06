"""
Features package initialization file.
This makes the features directory a proper Python package.
"""

# Import feature functions here to make them available at the package level
from .image_compressor import compress_image

__all__ = ['compress_image']
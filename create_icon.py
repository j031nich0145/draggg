#!/usr/bin/env python3
"""
Create a simple smiley face icon for draggg.
Generates a 256x256 PNG icon with a friendly smiley face.
"""

from PIL import Image, ImageDraw
import os
from pathlib import Path

def create_smiley_icon(output_path="assets/icon.png", size=256):
    """Create a smiley face icon."""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle (light blue/teal)
    bg_color = (70, 150, 200, 255)  # Nice teal color
    margin = size // 20
    draw.ellipse([margin, margin, size-margin, size-margin], fill=bg_color, outline=(50, 130, 180, 255), width=3)
    
    # Face circle (slightly smaller, cream/light yellow)
    face_margin = size // 10
    face_color = (255, 240, 200, 255)  # Cream color
    draw.ellipse([face_margin, face_margin, size-face_margin, size-face_margin], fill=face_color)
    
    # Three eyes - evenly spaced and symmetric
    eye_size = size // 8
    eye_y = size // 2.5
    
    # Calculate positions for three evenly spaced eyes
    # Left eye
    left_eye_x = size // 3.2
    draw.ellipse([left_eye_x - eye_size//2, eye_y - eye_size//2,
                  left_eye_x + eye_size//2, eye_y + eye_size//2], fill=(50, 50, 50, 255))
    
    # Middle eye (third eye - centered)
    middle_eye_x = size // 2
    draw.ellipse([middle_eye_x - eye_size//2, eye_y - eye_size//2,
                  middle_eye_x + eye_size//2, eye_y + eye_size//2], fill=(50, 50, 50, 255))
    
    # Right eye
    right_eye_x = size - size // 3.2
    draw.ellipse([right_eye_x - eye_size//2, eye_y - eye_size//2,
                  right_eye_x + eye_size//2, eye_y + eye_size//2], fill=(50, 50, 50, 255))
    
    # Smile (arc)
    smile_y = size // 1.6
    smile_width = size // 3
    smile_height = size // 5
    smile_left = size // 2 - smile_width // 2
    smile_right = size // 2 + smile_width // 2
    smile_top = smile_y - smile_height // 2
    smile_bottom = smile_y + smile_height // 2
    
    # Draw smile arc (bottom half of ellipse)
    draw.arc([smile_left, smile_top, smile_right, smile_bottom], 
             start=0, end=180, fill=(50, 50, 50, 255), width=size//25)
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"Icon created: {output_path} ({size}x{size})")

if __name__ == '__main__':
    # Create main icon
    create_smiley_icon("assets/icon.png", 256)
    
    # Also create smaller versions for different use cases
    create_smiley_icon("assets/icon-128.png", 128)
    create_smiley_icon("assets/icon-64.png", 64)
    create_smiley_icon("assets/icon-48.png", 48)
    
    print("\nIcons created successfully!")


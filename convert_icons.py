"""
Icon Converter Script
Converts PNG images to multi-size ICO files for Windows icons
"""

import os
import sys
from PIL import Image

def create_ico_from_png(png_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Convert PNG to ICO with multiple sizes."""
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Convert RGBA to RGB if needed (ICO format requirements)
        if img.mode == 'RGBA':
            # Create a white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create list of resized images
        images = []
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            images.append(resized)
        
        # Save as ICO file with multiple sizes
        img.save(ico_path, format='ICO', sizes=[(s, s) for s in sizes])
        print(f"✓ Created {ico_path} with sizes: {', '.join(map(str, sizes))}")
        return True
    except Exception as e:
        print(f"✗ Error converting {png_path}: {e}")
        return False

def main():
    """Convert all icon PNGs to ICO format."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Icon mapping: source PNG name -> output ICO name
    icon_mappings = [
        ("installer_icon.png", "installer_icon.ico"),  # For installer EXEs
        ("gui_icon.png", "gui_icon.ico"),              # For GUI EXE and taskbar
        ("shortcut_icon.png", "shortcut_icon.ico"),    # For desktop shortcuts
    ]
    
    # Also check for alternative names the user might use
    # "3386 life support" -> installer_icon
    # "smonker" -> gui_icon  
    # "screenshot" -> shortcut_icon
    
    alt_mappings = [
        ("3386_life_support.png", "installer_icon.ico"),
        ("3386_life_support.jpg", "installer_icon.ico"),
        ("3386_life_support.jpeg", "installer_icon.ico"),
        ("smonker.png", "gui_icon.ico"),
        ("smonker.jpg", "gui_icon.ico"),
        ("smonker.jpeg", "gui_icon.ico"),
        ("screenshot.png", "shortcut_icon.ico"),
        ("screenshot.jpg", "shortcut_icon.ico"),
        ("screenshot.jpeg", "shortcut_icon.ico"),
        ("desktop_shortcut.png", "shortcut_icon.ico"),
        ("desktop_shortcut.jpg", "shortcut_icon.ico"),
    ]
    
    print("=" * 60)
    print("Icon Converter - PNG to ICO")
    print("=" * 60)
    print()
    
    converted = 0
    
    # Try standard names first
    for png_name, ico_name in icon_mappings:
        png_path = os.path.join(base_dir, png_name)
        ico_path = os.path.join(base_dir, ico_name)
        
        if os.path.exists(png_path):
            if create_ico_from_png(png_path, ico_path):
                converted += 1
            print()
        else:
            print(f"⚠ {png_name} not found, skipping...")
    
    # Try alternative names
    for png_name, ico_name in alt_mappings:
        png_path = os.path.join(base_dir, png_name)
        ico_path = os.path.join(base_dir, ico_name)
        
        if os.path.exists(png_path) and not os.path.exists(ico_path):
            if create_ico_from_png(png_path, ico_path):
                converted += 1
            print()
    
    print("=" * 60)
    if converted > 0:
        print(f"✓ Converted {converted} icon file(s)")
        print()
        print("Created ICO files:")
        for _, ico_name in icon_mappings:
            ico_path = os.path.join(base_dir, ico_name)
            if os.path.exists(ico_path):
                size = os.path.getsize(ico_path)
                print(f"  - {ico_name} ({size/1024:.1f} KB)")
    else:
        print("⚠ No icons were converted")
        print()
        print("Please place your icon PNG files in this directory:")
        print("  - installer_icon.png (or 3386_life_support.png)")
        print("  - gui_icon.png (or smonker.png)")
        print("  - shortcut_icon.png (or screenshot.png)")
    print("=" * 60)

if __name__ == "__main__":
    main()

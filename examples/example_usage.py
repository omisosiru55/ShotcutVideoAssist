#!/usr/bin/env python3
"""
Basic usage example for mltpy

This example demonstrates:
1. Creating an MLTEditor instance
2. Adding various types of clips
3. Saving the modified MLT file
"""

from pathlib import Path
from mltpy import MLTEditor

def main():
    # Sample MLT file path (adjust as needed)
    input_mlt = "sample_project.mlt"
    
    if not Path(input_mlt).exists():
        print(f"MLT file not found: {input_mlt}")
        print("Please create a sample MLT file or adjust the path")
        return
    
    try:
        # Create editor instance
        print(f"Loading MLT file: {input_mlt}")
        editor = MLTEditor(input_mlt, playlist_id=4)
        
        # Set output path
        output_path = editor.set_output_path("basic_example")
        print(f"Output will be saved to: {output_path}")
        
        # Get project information
        width, height = editor.project_size
        print(f"Project resolution: {width}x{height}")
        
        # Add a video clip (adjust path as needed)
        video_path = "sample_video.mp4"
        if Path(video_path).exists():
            print("Adding video clip...")
            editor.add_video_clip(video_path, speed=1.5)
        else:
            print(f"Video file not found: {video_path}, skipping...")
        
        # Add an image clip
        image_path = "sample_image.jpg"
        if Path(image_path).exists():
            print("Adding image clip...")
            editor.add_image_clip(image_path, duration="00:00:03.000")
        else:
            print(f"Image file not found: {image_path}, skipping...")
        
        # Add text overlay
        print("Adding text overlay...")
        editor.add_text_overlay("Created with mltpy!")
        
        # Save the modified MLT file
        print("Saving modified MLT file...")
        editor.save()
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

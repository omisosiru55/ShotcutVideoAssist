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
from mltpy.exceptions import MLTFileNotFoundError, MLTParseError

def main():
    # Sample MLT file path (adjust as needed)
    input_mlt = r"C:\Users\aaa\OneDrive\Desktop\test.mlt"
    
    try:
        # Create editor instance
        print(f"Loading MLT file: {input_mlt}")
        editor = MLTEditor(input_mlt, playlist_id=3)
        
        # Set output path
        output_path = editor.set_output_path("edited")
        print(f"Output will be saved to: {output_path}")
        
        # Get project information
        width, height = editor.project_size
        print(f"Project resolution: {width}x{height}")
        
        # Save the modified MLT file
        print("Saving modified MLT file...")
        editor.save()
        print("Done!")

    except MLTFileNotFoundError as e:
        print(f"Error: {e}")
        print("Please create a sample MLT file or adjust the path.")
    except MLTParseError as e:
        print(f"Error: Could not parse the MLT file. It might be corrupted.")
        print(f"Details: {e}")
    except Exception as e:
        # その他の予期せぬエラー
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
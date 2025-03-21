import os
import sys
import time
from pathlib import Path
try:
    from aksharamukha import transliterate
except ImportError:
    print("Aksharamukha package not found. Installing...")
    os.system("pip install aksharamukha-python==2.1.1")
    from aksharamukha import transliterate

def get_available_scripts():
    """Returns a list of all available scripts in Aksharamukha."""
    return transliterate.get_available_scripts()

def transliterate_text(text, source_script, target_script):
    """
    Transliterate text from source script to target script.
    
    Args:
        text (str): Text to transliterate
        source_script (str): Source script name
        target_script (str): Target script name
    
    Returns:
        str: Transliterated text
    """
    try:
        return transliterate.process(source_script, target_script, text)
    except Exception as e:
        print(f"Error during transliteration: {e}")
        return None

def transliterate_file(input_file, output_file, source_script, target_script):
    """
    Transliterate content of a file from source script to target script.
    
    Args:
        input_file (str): Path to input file
        output_file (str): Path to output file
        source_script (str): Source script name
        target_script (str): Target script name
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_file).parent
        os.makedirs(output_path, exist_ok=True)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        transliterated_text = transliterate_text(text, source_script, target_script)
        
        if transliterated_text is None:
            return False
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transliterated_text)
        
        return True
    except Exception as e:
        print(f"Error transliterating file: {e}")
        return False

if __name__ == "__main__":
    print("Available scripts:", get_available_scripts())
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
    # The get_available_scripts() method doesn't exist in the aksharamukha library
    # Instead, we can access the available scripts from the Transliterator's db attribute
    trans = transliterate.Transliterator()
    return sorted(list(trans.db.keys()))

def transliterate_text(text, source_script, target_script):
    try:
        return transliterate.process(source_script, target_script, text)
    except Exception as e:
        print(f"Error during transliteration: {e}")
        return None

def transliterate_file(input_file, output_file, source_script, target_script):
    try:
        output_path = Path(output_file).parent
        os.makedirs(output_path, exist_ok=True)
        
        with open(input_file, 'r', encoding='utf-8') as input_f, \
             open(output_file, 'w', encoding='utf-8') as output_f:
            
            for line in input_f:
                # Process each line
                transliterated_line = transliterate_text(line, source_script, target_script)
                
                if transliterated_line is None:
                    print(f"Error transliterating line: {line.strip()}")
                    return False
                
                # Write the transliterated line to output file
                output_f.write(transliterated_line)
        
        return True
    except Exception as e:
        print(f"Error transliterating file: {e}")
        return False

if __name__ == "__main__":
    print("Available scripts:", get_available_scripts()) # List available scripts
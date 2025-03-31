import os
import sys
import time
from pathlib import Path
import requests
from urllib.parse import quote

# Try to import all supported transliteration libraries
try:
    from aksharamukha import transliterate as aksharamukha_transliterate
except ImportError:
    print("Aksharamukha package not found. Installing...")
    os.system("pip install aksharamukha-python==2.1.1")
    from aksharamukha import transliterate as aksharamukha_transliterate

try:
    from indic_transliteration import sanscript
    INDIC_AVAILABLE = True
except ImportError:
    print("Indic-transliteration package not found. Installing...")
    os.system("pip install indic-transliteration")
    try:
        from indic_transliteration import sanscript
        INDIC_AVAILABLE = True
    except ImportError:
        INDIC_AVAILABLE = False

def get_available_scripts():
    """Get all available scripts across all supported libraries"""
    scripts = set()
    
    # Aksharamukha scripts
    trans = aksharamukha_transliterate.Transliterator()
    scripts.update(sorted(list(trans.db.keys())))
    
    # Add Indic-transliteration scripts if available
    if INDIC_AVAILABLE:
        for scheme_name in sanscript.SCHEMES:
            scripts.add(scheme_name)
    
    return sorted(list(scripts))

def transliterate_text(text, source_script, target_script, system="aksharamukha"):
    """
    Transliterate text using the specified system
    
    Args:
        text: The text to transliterate
        source_script: Source script name
        target_script: Target script name
        system: Transliteration system to use ("aksharamukha", "indic_transliteration", or "google")
        
    Returns:
        Transliterated text or None if an error occurred
    """
    try:
        if system == "aksharamukha":
            return aksharamukha_transliterate.process(source_script, target_script, text)
        
        elif system == "indic_transliteration" and INDIC_AVAILABLE:
            # Map script names to Indic-transliteration scheme constants
            script_map = {
                "IAST": sanscript.IAST,
                "Devanagari": sanscript.DEVANAGARI,
                "Telugu": sanscript.TELUGU,
                "Bengali": sanscript.BENGALI,
                "Gujarati": sanscript.GUJARATI,
                "Kannada": sanscript.KANNADA,
                "Malayalam": sanscript.MALAYALAM,
                "Oriya": sanscript.ORIYA,
                "Tamil": sanscript.TAMIL,
                # Add more mappings as needed
            }
            
            src = script_map.get(source_script, source_script)
            tgt = script_map.get(target_script, target_script)
            
            return sanscript.transliterate(text, src, tgt)
        
        elif system == "google":
            # Map script names to Google's language codes
            lang_map = {
                "Devanagari": "hi",
                "Telugu": "te",
                "Bengali": "bn",
                "Gujarati": "gu",
                "Kannada": "kn",
                "Malayalam": "ml",
                "Tamil": "ta",
                # Add more mappings as needed
            }
            
            # Only supports IAST to target script conversion
            if source_script == "IAST" and target_script in lang_map:
                lang_code = lang_map[target_script]
                try:
                    # Fixed format according to Google's API requirements
                    url = "https://inputtools.google.com/request"
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    # Correct payload structure as required by Google API
                    payload = [
                        "transliterate",
                        {
                            "langpair": f"sa|{lang_code}",
                            "text": text.strip()
                        }
                    ]
                    
                    # Print request details for debugging
                    print(f"Sending request to Google API...")
                    print(f"URL: {url}")
                    print(f"Headers: {headers}")
                    print(f"Payload: {payload}")
                    
                    response = requests.post(url, json=payload, headers=headers)
                    print(f"Response status: {response.status_code}")
                    print(f"Response content: {response.text[:200]}...")
                    
                    result = response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        return result[0][1][0]
                    else:
                        print(f"Unexpected response format: {result}")
                        return None
                except Exception as e:
                    print(f"Google API error: {e}")
                    return None
            
            # For unsupported conversions, return None instead of falling back
            print(f"Google API does not support conversion from {source_script} to {target_script}")
            return None
            
    except Exception as e:
        print(f"Error during transliteration with {system}: {e}")
        return None

def transliterate_file(input_file, output_file, source_script, target_script, system="aksharamukha"):
    """
    Transliterate all text in a file
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        source_script: Source script name
        target_script: Target script name
        system: Transliteration system to use
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_file).parent
        os.makedirs(output_path, exist_ok=True)
        
        print(f"Transliterating from {source_script} to {target_script} using {system}...")
        
        with open(input_file, 'r', encoding='utf-8') as input_f, \
             open(output_file, 'w', encoding='utf-8') as output_f:
            
            for line in input_f:
                # Process each line
                transliterated_line = transliterate_text(line, source_script, target_script, system)
                
                if transliterated_line is None:
                    print(f"Error transliterating line: {line.strip()}")
                    return False
                
                # Write the transliterated line to output file
                output_f.write(transliterated_line)
        
        return True
    except Exception as e:
        print(f"Error transliterating file: {e}")
        return False

def get_available_systems():
    """Return a list of available transliteration systems"""
    systems = ["aksharamukha"]
    
    if INDIC_AVAILABLE:
        systems.append("indic_transliteration")
    
    # Remove Google as it's not working properly with our implementation
    # systems.append("google")
    
    return systems

if __name__ == "__main__":
    print("Available scripts:", get_available_scripts()) # List available scripts
    print("Available systems:", get_available_systems()) # List available systems
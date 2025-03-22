import os
import argparse
from pathlib import Path
import time
import datetime
from transliterator import transliterate_file, get_available_scripts
from compare_texts import compare_files

def create_output_filename(input_file, script, output_dir=None):

    input_path = Path(input_file)
    base_name = input_path.stem
    
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path.parent / "transliterated"
    
    os.makedirs(output_path, exist_ok=True)
    
    return str(output_path / f"{base_name}_{script.lower()}{input_path.suffix}")

def run_transliteration_pipeline(input_file, output_dir=None, log_dir=None):
    """
    Run full transliteration pipeline: IAST → Devanagari → IAST and compare.
    
    Args:
        input_file (str): Path to input file in IAST
        output_dir (str, optional): Directory for output files. Defaults to None.
        log_dir (str, optional): Directory for log files. Defaults to None.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Starting transliteration pipeline for {input_file}")
        start_time = time.time()
        
        # Set up directories
        if not output_dir:
            output_dir = Path(input_file).parent / "transliterated"
        else:
            output_dir = Path(output_dir)
        
        if not log_dir:
            log_dir = Path("logfiles")
        else:
            log_dir = Path(log_dir)
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # File paths
        input_base = Path(input_file).stem
        devanagari_file = str(output_dir / f"{input_base}_devanagari.txt")
        back_to_iast_file = str(output_dir / f"{input_base}_back_to_iast.txt")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = str(log_dir / f"transliteration_comparison_{timestamp}.log")
        
        # Step 1: IAST to Devanagari
        print("Step 1: Transliterating from IAST to Devanagari...")
        if not transliterate_file(input_file, devanagari_file, "IAST", "Devanagari"):
            print("Failed to transliterate from IAST to Devanagari")
            return False
        
        # Step 2: Devanagari back to IAST
        print("Step 2: Transliterating from Devanagari back to IAST...")
        if not transliterate_file(devanagari_file, back_to_iast_file, "Devanagari", "IAST"):
            print("Failed to transliterate from Devanagari back to IAST")
            return False
        
        print("Step 3: Comparing original and transliterated text...")
        if not compare_files(input_file, back_to_iast_file, log_file):
            print("Failed to compare files")
            return False
        
        elapsed_time = time.time() - start_time
        print(f"Transliteration pipeline completed in {elapsed_time:.2f} seconds")
        print(f"Results saved to {log_file}")
        
        return True
    except Exception as e:
        print(f"Error in transliteration pipeline: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Transliterate text and compare results")
    parser.add_argument("input_file", help="Input file in IAST script")
    parser.add_argument("--output-dir", help="Directory for output files")
    parser.add_argument("--log-dir", help="Directory for log files")
    parser.add_argument("--list-scripts", action="store_true", help="List available scripts")
    
    args = parser.parse_args()
    
    if args.list_scripts:
        scripts = get_available_scripts()
        print("Available scripts:")
        for script in sorted(scripts):
            print(f"- {script}")
        return
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist")
        return
    
    success = run_transliteration_pipeline(args.input_file, args.output_dir, args.log_dir)
    if not success:
        print("Transliteration pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()
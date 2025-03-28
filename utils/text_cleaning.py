import re
import sys

def clean_text(input_file, output_file):
    au_pattern = r'\[\.{3} au\d*[^\]]*\]'

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
                open(output_file, 'w', encoding='utf-8') as outfile:

            for line in infile:
                cleaned_line = re.sub(au_pattern, '', line)
                cleaned_line = re.sub(r'\.+', '', cleaned_line)
                outfile.write(cleaned_line)

        print(f"Text cleaning completed. Output saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found.")
    except PermissionError:
        print(f"Error: Permission denied when trying to read {input_file} or write to {output_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    clean_text(input_file, output_file)

if __name__ == "__main__":
    main()
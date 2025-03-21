import os
import glob


def merge_txt_files(input_directory, output_file):
    """
    Merge all .txt files in the specified directory into a single output file
    without adding file headers.

    Args:
        input_directory (str): Path to the directory containing .txt files
        output_file (str): Path where the merged file will be saved
    """
    txt_files = glob.glob(os.path.join(input_directory, "*.txt"))

    if not txt_files:
        print(f"No .txt files found in {input_directory}")
        return

    print(f"Found {len(txt_files)} .txt files to merge.")

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_num, file_path in enumerate(txt_files, 1):
            file_name = os.path.basename(file_path)
            print(f"Processing file {file_num}/{len(txt_files)}: {file_name}")

            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

    print(f"All files successfully merged into {output_file}")

if __name__ == "__main__":
    input_dir = "data/raw/FinalCorpus"
    output_file = "../data/cleaned/merged_output.txt"
    merge_txt_files(input_dir, output_file)
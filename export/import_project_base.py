import os
import tkinter as tk
from tkinter import filedialog

def parse_directory_structure_and_code(input_file):
    """
    Parse the text file containing directory structure and code.
    Returns a tuple of (directory_structure, all_code) where:
    - directory_structure is a list of directory/file paths
    - all_code is a dict mapping file paths to their content
    """
    with open(input_file, 'r') as infile:
        content = infile.read()

    directory_structure = []
    all_code = {}
    current_file_path = None
    file_lines = []

    lines = content.splitlines()
    for line in lines:
        if line.startswith('# File: '):
            if current_file_path and file_lines:
                all_code[current_file_path] = '\n'.join(file_lines)
                print(f"Stored code for file: {current_file_path}")
            current_file_path = line[7:].strip()  # Extract file path from '# File: '
            file_lines = []
            print(f"Found file path: {current_file_path}")
        elif current_file_path is not None:
            file_lines.append(line)
        else:
            directory_structure.append(line)
            print(f"Added directory or file entry: {line}")

    # Don't forget the last file
    if current_file_path and file_lines:
        all_code[current_file_path] = '\n'.join(file_lines)
        print(f"Stored code for file: {current_file_path}")

    return directory_structure, all_code

def create_directories(directory_structure):
    """Create all necessary directories from the structure."""
    for line in directory_structure:
        dir_path = line.strip().rstrip('/')
        if dir_path and not os.path.splitext(dir_path)[1]:  # Only create if it's not a file
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")

def write_code_files(all_code):
    """Write the code content to their respective files."""
    for file_path, code in all_code.items():
        # Create directories for the file if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as outfile:
            outfile.write(code)
        print(f"Written code to file: {file_path}")

def select_file():
    """Open a file dialog to select the project structure text file."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select the project txt file",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    return file_path

if __name__ == "__main__":
    input_file = select_file()
    if input_file:
        print(f"Selected file: {input_file}")
        directory_structure, all_code = parse_directory_structure_and_code(input_file)
        print(f"Directory structure: {directory_structure}")
        print(f"All code files: {list(all_code.keys())}")
        create_directories(directory_structure)
        write_code_files(all_code)
        print("Completed processing the project file.")
    else:
        print("No file selected.")
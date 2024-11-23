import os

def generate_directory_structure(root_dir, ignore_dirs=None):
    ignore_dirs = ignore_dirs or []
    directory_structure = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs and d != '__pycache__']
        level = dirpath.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        directory_structure.append(f'{indent}{os.path.basename(dirpath)}/\n')
        sub_indent = ' ' * 4 * (level + 1)
        for fname in filenames:
            if not fname.endswith('.pyc'):
                directory_structure.append(f'{sub_indent}{fname}\n')
    return ''.join(directory_structure)

def concatenate_code_files(root_dir, file_extension='.py', exclude_files=None):
    exclude_files = exclude_files or []
    script_name = os.path.basename(__file__)
    exclude_files.append(script_name)
    
    all_code = []
    for dirpath, _, filenames in os.walk(root_dir):
        if '__pycache__' in dirpath:
            continue
        for fname in filenames:
            if fname.endswith(file_extension) and fname not in exclude_files and not fname.endswith('.pyc'):
                filepath = os.path.join(dirpath, fname)
                with open(filepath, 'r') as infile:
                    all_code.append(f'# File: {filepath}\n')
                    all_code.append(infile.read())
                    all_code.append('\n\n')
    return ''.join(all_code)

def combine_files(output_file, directory_structure='', all_code=''):
    with open(output_file, 'w') as outfile:
        outfile.write(directory_structure)
        outfile.write('\n\n')
        outfile.write(all_code)

if __name__ == "__main__":
    project_directory = "C:\\Users\\galaxy\\Documents\\VsCode\\DeepStats"  # Project directory path
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_directory, 'existing_project_structure.txt')
    exclude_files = ['export_project.py']  # File to be excluded
    directory_structure = generate_directory_structure(project_directory, ignore_dirs=['node_modules', '.git', 'dist'])
    all_code = concatenate_code_files(project_directory, file_extension='.py', exclude_files=exclude_files)
    combine_files(output_file, directory_structure=directory_structure, all_code=all_code)

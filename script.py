import json
import re
import os
import shutil

# Define the source directory
source_dir = '.'  # Current directory

# Load rules from clopen.json
clopen_config_path = os.path.join(source_dir, 'clopen.json')
with open(clopen_config_path, 'r') as file:
    config = json.load(file)

# Prepare regex patterns for removal and replacement
to_remove_patterns = [re.compile(re.escape(path)) for path in config['toRemove']]
to_replace_patterns = {re.compile(pattern): repl for pattern, repl in config['toReplace'].items()}

def remove_files_and_directories(source_dir, to_remove_patterns):
    for root, dirs, files in os.walk(source_dir, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if any(pattern.search(dir_path) for pattern in to_remove_patterns):
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dir_path}")
        for file in files:
            file_path = os.path.join(root, file)
            if any(pattern.search(file_path) for pattern in to_remove_patterns):
                os.remove(file_path)
                print(f"Removed file: {file_path}")

def sanitize_content(content, to_replace_patterns):
    for pattern, replacement in to_replace_patterns.items():
        content = pattern.sub(replacement, content)
    return content

def file_should_be_copied(file_path, to_remove_patterns):
    return not any(pattern.search(file_path) for pattern in to_remove_patterns)

def sanitize_files(source_dir, to_replace_patterns):
    for root, dirs, files in os.walk(source_dir):
        # Remove directories that should not be copied
        dirs[:] = [d for d in dirs if file_should_be_copied(os.path.join(root, d), to_remove_patterns)]
        for file in files:
            file_path = os.path.join(root, file)
            if file_should_be_copied(file_path, to_remove_patterns):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Skip files that cannot be read as UTF-8 text
                    print(f"Skipping file (non-text or unknown encoding): {file_path}")
                    continue

                # Sanitize the content
                content = sanitize_content(content, to_replace_patterns)

                # Write the sanitized content back to the source file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

# Remove specified files and directories first
remove_files_and_directories(source_dir, to_remove_patterns)

# Start the sanitization process
sanitize_files(source_dir, to_replace_patterns)

print("Sanitization complete. Files in '{}' have been sanitized.".format(source_dir))

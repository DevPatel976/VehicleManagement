import os
import re

def remove_comments_from_file(file_path):
    """Remove all comments from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove single line comments
    content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
    
    # Remove multi-line comments
    content = re.sub(r'"""[\s\S]*?"""', '', content)
    content = re.sub(r"'''[\s\S]*?'''", '', content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def process_directory(directory):
    """Process all Python files in a directory and its subdirectories."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                remove_comments_from_file(file_path)

if __name__ == "__main__":
    # Set the directory to process - current directory by default
    directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Removing comments from Python files in: {directory}")
    process_directory(directory)
    print("Comment removal completed.")

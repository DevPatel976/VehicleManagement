import os
import re
from pathlib import Path
def remove_comments_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = re.sub(r'
    content = re.sub(r'', '', content)
    content = re.sub(r"", '', content)
    content = '\n'.join(line for line in content.split('\n') if line.strip())
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                remove_comments_from_file(file_path)
if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))
    process_directory(project_dir)
    print("All Python files have been processed and comments removed.")
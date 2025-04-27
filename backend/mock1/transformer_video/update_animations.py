import os
import re

def replace_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace ShowCreation with Create
    updated_content = re.sub(r'ShowCreation', 'Create', content)
    
    # Write back to the file if changes were made
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"Updated: {file_path}")

def main():
    # Get all Python files in the current directory
    for filename in os.listdir('.'):
        if filename.endswith('.py') and not filename == 'update_animations.py':
            replace_in_file(filename)
    
    print("Animation updates complete!")

if __name__ == "__main__":
    main() 
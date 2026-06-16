import csv
import os
import re

def create_student_files(csv_filename: str, output_dir: str = "student_repos"):
    """
    Create individual .txt files for each student with their GitHub repo link.
    
    Args:
        csv_filename: Path to the submission_metadata.csv file
        output_dir: Directory to create the .txt files in
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the CSV file
    students = []
    with open(csv_filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only process students with a valid email and GitHub link
            if row.get('Email') and row.get('Question 1 Response'):
                email = row['Email'].strip().lower()
                github_link = row['Question 1 Response'].strip()
                
                # Validate email format
                if '@' in email and github_link and github_link != 'Missing':
                    students.append({
                        'email': email,
                        'github': github_link,
                        'first_name': row.get('First Name', ''),
                        'last_name': row.get('Last Name', '')
                    })
    
    # Create individual files
    created_files = []
    for student in students:
        filename = os.path.join(output_dir, student['email'])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(student['github'] + '\n')
        created_files.append(filename)
        print(f"Created: {filename} -> {student['github']}")
    
    print(f"\nTotal files created: {len(created_files)}")
    return created_files

def extract_github_links_from_csv(csv_filename: str, output_dir: str = "student_repos"):
    """
    Alternative function that only extracts GitHub links without email validation.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    with open(csv_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by rows and process
    lines = content.strip().split('\n')
    header = lines[0].split(',')
    
    # Find indices of Email and GitHub Response columns
    email_idx = None
    github_idx = None
    
    for i, col in enumerate(header):
        if col == 'Email':
            email_idx = i
        elif col == 'Question 1 Response':
            github_idx = i
    
    created_files = []
    
    for line in lines[1:]:
        # Handle CSV with commas in fields (simple parsing)
        parts = []
        current = ''
        in_quotes = False
        
        for char in line:
            if char == '"' and not in_quotes:
                in_quotes = True
            elif char == '"' and in_quotes:
                in_quotes = False
            elif char == ',' and not in_quotes:
                parts.append(current)
                current = ''
            else:
                current += char
        parts.append(current)  # Add last field
        
        # Clean up parts
        parts = [p.strip().strip('"') for p in parts]
        
        if email_idx is not None and github_idx is not None:
            email = parts[email_idx].strip().lower() if email_idx < len(parts) else ''
            github = parts[github_idx].strip() if github_idx < len(parts) else ''
            
            if email and '@' in email and github and github != 'Missing':
                filename = os.path.join(output_dir, email)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(github + '\n')
                created_files.append(filename)
                print(f"Created: {filename}")
    
    print(f"\nTotal files created: {len(created_files)}")
    return created_files

def verify_files(output_dir: str = "student_repos"):
    """Verify all created files and show their contents."""
    print("\n" + "="*50)
    print("VERIFYING CREATED FILES")
    print("="*50)
    
    files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    
    for filename in sorted(files):
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        print(f"\n{filename}:")
        print(f"  {content}")
    
    print(f"\nTotal: {len(files)} files created in '{output_dir}/'")

if __name__ == "__main__":
    # Use the first function (with email validation)
    csv_file = "submission_metadata.csv"
    
    if os.path.exists(csv_file):
        # Create individual files
        created = create_student_files(csv_file)
        
        # Verify the files
        verify_files()
        
        # Optional: Create a summary file
        with open("student_repos_summary.txt", 'w', encoding='utf-8') as summary:
            for student_file in created:
                with open(student_file, 'r', encoding='utf-8') as f:
                    repo = f.read().strip()
                email = os.path.basename(student_file)
                summary.write(f"{email}: {repo}\n")
        
        print(f"\nSummary file created: student_repos_summary.txt")
    else:
        print(f"Error: {csv_file} not found!")
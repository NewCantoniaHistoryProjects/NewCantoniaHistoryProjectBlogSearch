import os
import json
from bs4 import BeautifulSoup

def generate_posts_data(input_folder="posts", output_file="posts_data.js"):
    posts = []
    
    # Ensure input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found")
        return
    
    # Scan all HTML files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(input_folder, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract title (first h1 or filename if no h1)
                title = soup.find('h1')
                title_text = title.get_text(strip=True) if title else filename
                
                # Extract all displayable text
                content_text = soup.get_text(strip=True)
                
                posts.append({
                    'title': title_text,
                    'file': filename,
                    'content': content_text
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
    
    # Generate JavaScript content
    js_content = f"const postsData = {json.dumps(posts, indent=2)};"
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Generated {output_file} with {len(posts)} posts")

if __name__ == "__main__":
    generate_posts_data()
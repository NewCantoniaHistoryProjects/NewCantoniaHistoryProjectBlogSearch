import os
import xml.etree.ElementTree as ET
import json
import re
from bs4 import BeautifulSoup

def parse_blogger_xml(xml_file):
    # Parse the XML file
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"Error: Could not find file '{xml_file}'")
        return []
    except Exception as e:
        print(f"Error parsing XML: {str(e)}")
        return []
    
    # Namespace handling (Blogger XML uses Atom feed format)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    
    # List to store results
    entries_data = []
    
    # Regex pattern to match 4-digit years
    year_pattern = r'\b(19|20)\d{2}\b'
    
    # Find all entry elements
    for entry in root.findall('.//atom:entry', namespace):
        # Look for link with specific prefix and rel="alternate"
        link_found = False
        link_href = None
        
        for link in entry.findall('atom:link', namespace):
            href = link.get('href')
            rel = link.get('rel')
            if (href and 
                href.startswith('https://newcantoniahistory.blogspot.com') and 
                rel == 'alternate'):
                link_found = True
                link_href = href
                break
        
        # Skip if no matching link found
        if not link_found:
            continue
            
        # Get content
        content_elem = entry.find('atom:content', namespace)
        content = content_elem.text if content_elem is not None else ''
        
        # Get title
        title_elem = entry.find('atom:title', namespace)
        title = title_elem.text if title_elem is not None else ''
        
        # Check if title contains a year
        if not re.search(year_pattern, title):
            print(f"Title without year found: '{title}'")
            print(f"Link: {link_href}")
            print("-" * 50)
        
        # Append entry data
        entries_data.append({
            'title': title,
            'content': content,
            'link': link_href
        })
    
    return entries_data

def parse_medium_html(input_folder="posts"):
    posts = []
    
    # Ensure input folder exists
    if not os.path.exists(input_folder):
        print(f"Warning: Folder '{input_folder}' not found, skipping Medium posts")
        return posts
    
    # Scan all HTML files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(input_folder, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find div with class "section-content"
                section_div = soup.find('div', class_='section-content')
                if not section_div:
                    print(f"Warning: No div.section-content found in {filename}")
                    continue
                
                # Extract title from h3 with class "graf--title"
                title_elem = section_div.find('h3', class_='graf--title')
                title_text = title_elem.get_text(strip=True) if title_elem else filename
                
                # Extract content from all p elements with class "graf--p"
                content_elems = section_div.find_all('p', class_='graf--p')
                content_text = ' '.join(elem.get_text(strip=True) for elem in content_elems) if content_elems else ''
                
                # Find footer element
                footer = soup.find('footer')
                if not footer:
                    print(f"Warning: No footer found in {filename}")
                    continue
                
                # Find link in footer with prefix "https://medium.com/p/"
                link_elem = footer.find('a', href=lambda href: href and href.startswith('https://medium.com/p/'))
                link_href = link_elem['href'] if link_elem else None
                
                if not link_href:
                    print(f"Warning: No Medium link found in footer of {filename}")
                    continue
                    
                # Append post data
                posts.append({
                    'title': title_text,
                    'content': content_text,
                    'link': link_href
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
    
    return posts

def main():
    # Input files and folder
    xml_file = 'blogger_export.xml'
    input_folder = 'posts'
    output_file = 'blogger_export.js'
    
    # Get Blogger posts
    blogger_posts = [] # parse_blogger_xml(xml_file)
    
    # Get Medium posts
    medium_posts = parse_medium_html(input_folder)
    
    # Combine all posts
    all_posts = blogger_posts + medium_posts
    
    # Generate JavaScript content
    try:
        js_content = f"const postsData = {json.dumps(all_posts, ensure_ascii=False, indent=2)};"
        
        # Write to JS file
        with open(output_file, 'w', encoding='utf-8') as js_file:
            js_file.write(js_content)
        
        print(f"\nSuccessfully processed {len(blogger_posts)} Blogger posts and {len(medium_posts)} Medium posts")
        print(f"Saved {len(all_posts)} total entries to {output_file}")
        
    except Exception as e:
        print(f"Error writing output file: {str(e)}")

if __name__ == "__main__":
    main()
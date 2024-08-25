import os
import requests
from bs4 import BeautifulSoup
import re

def read_items_from_files():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    workshop_items = []
    mod_ids = []
    
    for filename in os.listdir(current_directory):
        if filename.endswith(".txt") or filename.endswith(".ini"):
            file_path = os.path.join(current_directory, filename)
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        line = line.strip()
                        if line.startswith('WorkshopItems='):
                            items = line[len('WorkshopItems='):].split(';')
                            workshop_items.extend(item.strip() for item in items if item.strip())
                        elif line.startswith('Mods='):
                            mods = line[len('Mods='):].split(';')
                            mod_ids.extend(mod.strip() for mod in mods if mod.strip())
            except FileNotFoundError:
                print(f"Error: {filename} file not found.")
    
    print(f"Workshop items: {workshop_items}")
    print()
    print(f"Mod IDs: {mod_ids}")
    print()
    return workshop_items, mod_ids

def extract_mod_ids_from_html(html_content, mod_ids):
    soup = BeautifulSoup(html_content, 'html.parser')
    mod_ids_found = set()
    
    description_div = soup.find('div', class_='workshopItemDescription')
    if description_div:
        text_content = description_div.get_text()
        
        # Updated patterns to match Mod IDs more precisely
        mod_id_patterns = [
            re.compile(r'Mod\s*ID:\s*([\w_]+)\s*$', re.MULTILINE | re.IGNORECASE),
            re.compile(r'ModID\s*:\s*([\w_]+)\s*$', re.MULTILINE | re.IGNORECASE)
        ]
        
        # Extract found Mod IDs using the patterns
        for pattern in mod_id_patterns:
            found_ids = pattern.findall(text_content)
            # Strip any extra spaces from found IDs
            found_ids = [id_.strip() for id_ in found_ids]
            mod_ids_found.update(found_ids)
        
        # Additionally, check for exact matches with mod_id variables
        for mod_id in mod_ids:
            if mod_id in text_content:
                mod_ids_found.add(mod_id)
    else:
        print("No div with class 'workshopItemDescription' found.")
    
    return mod_ids_found

def check_urls(workshop_items, mod_ids):
    if not workshop_items:
        return
    
    base_url = "https://steamcommunity.com/workshop/filedetails/?id="
    
    ids = [item_id for item_id in workshop_items if item_id.isdigit()]
    
    not_found_mod_ids = set(mod_ids)
    
    for item_id in ids:
        url = f"{base_url}{item_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.title.string if soup.title else 'No Title Found'
            
            if "Steam Community :: Error" in title:
                print(f"Invalid (Error Page): {url}")
            elif "obsolete" in title.lower():
                print(f"Warning: {url} -> Title: {title}")
            else:
                print(f"Valid: {url} -> Title: {title}")
                
                page_mod_ids = extract_mod_ids_from_html(html_content, mod_ids)
                
                if page_mod_ids:
                    print(f"Mod IDs found on page: {page_mod_ids}")
                    
                    for mod_id in mod_ids:
                        if mod_id in page_mod_ids:
                            print(f"Matching Mod ID found in provided IDs: -> Mod ID: {mod_id}")
                            if mod_id in not_found_mod_ids:
                                not_found_mod_ids.remove(mod_id)
                else:
                    print(f"Mod ID NOT FOUND: {url}")
        
        except Exception as e:
            print(f"Error: {url} -> {e}")
        
        print()  # Newline to separate different URLs

    # List any mod IDs not found
    if not_found_mod_ids:
        print("Mod IDs not found:")
        for mod_id in not_found_mod_ids:
            print(mod_id)

# Read workshop items and mod IDs from all .txt and .ini files in the directory
workshop_items, mod_ids = read_items_from_files()

# Run the URL check
check_urls(workshop_items, mod_ids)

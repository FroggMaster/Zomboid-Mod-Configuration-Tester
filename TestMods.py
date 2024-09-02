import os
import sys
import requests
from bs4 import BeautifulSoup
import re

DEBUG = '-d' in sys.argv

def read_items_from_files(file_path=None):
    if file_path:
        # Read from the specified file path
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                workshop_items = []
                mod_ids = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('WorkshopItems='):
                        items = line[len('WorkshopItems='):].split(';')
                        workshop_items.extend(item.strip() for item in items if item.strip())
                    elif line.startswith('Mods='):
                        mods = line[len('Mods='):].split(';')
                        mod_ids.extend(mod.strip() for mod in mods if mod.strip())
                
                if DEBUG:
                    print(f"Workshop items: {workshop_items}")
                    print()
                    print(f"Mod IDs: {mod_ids}")
                    print()
                
                return workshop_items, mod_ids

        except FileNotFoundError:
            print(f"Error: {file_path} file not found.")
            return [], []
    else:
        # Read from all .txt and .ini files in the current directory
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
        
        if DEBUG:
            print(f"Workshop items: {workshop_items}")
            print()
            print(f"Mod IDs: {mod_ids}")
            print()
        
        return workshop_items, mod_ids
    
def preprocess_text_for_mod_ids(text_content):
    # Replace 'Mod ID:' with a new line followed by 'Mod ID:'
    cleaned_text = re.sub(r'\s*Mod\s*ID\s*:\s*(?=\w)', '\nMod ID:', text_content).strip()
    # Ensure any trailing text after a Mod ID is separated
    cleaned_text = re.sub(r'(Mod ID:\s*\w+)\s*(?::\s*\w+)', r'\1', cleaned_text)
    # Replace 'Workshop ID:' with a new line followed by 'Workshop ID:'
    cleaned_text = re.sub(r'\s*Workshop\s*ID\s*:\s*', '\nWorkshop ID:\n', cleaned_text)
    # Ensure there are no extra new lines and spaces
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text).strip()
    return cleaned_text

def extract_mod_ids_from_html(html_content, mod_ids):
    soup = BeautifulSoup(html_content, 'html.parser')
    mod_ids_found = set()
    
    description_div = soup.find('div', class_='workshopItemDescription')
    if description_div:
        # Replace <br> tags with newline characters
        for br in description_div.find_all("br"):
            br.replace_with("\n")

        # Now extract the text content
        text_content = description_div.get_text()

        if DEBUG:
            print("Extracted text content:")
            print(text_content)
            print()  # Newline for readability

        # Preprocess the text content
        cleaned_text = preprocess_text_for_mod_ids(text_content)

        if DEBUG:
            print("Preprocessed text content:")
            print(cleaned_text)
            print()  # Newline for readability

        # Updated pattern to capture valid Mod IDs only
        pattern = re.compile(r'\bMod\s*ID\s*:\s*([A-Za-z0-9_-]+)\b', re.IGNORECASE)

        # Extract all found Mod IDs using the updated pattern
        found_ids = pattern.findall(cleaned_text)
        if DEBUG:
            print(f"Found IDs: {found_ids}")

        # Strip any extra spaces from found IDs and add to set
        found_ids = [id_.strip() for id_ in found_ids]
        mod_ids_found.update(found_ids)
                
        if DEBUG:
            print("Final Mod IDs found:")
            print(mod_ids_found)
            print()  # Newline for readability
    else:
        print("No div with class 'workshopItemDescription' found.")
    
    return mod_ids_found

def check_urls(workshop_items, mod_ids):
    if not workshop_items and not mod_ids:
        return

    base_url = "https://steamcommunity.com/workshop/filedetails/?id="

    ids = [item_id for item_id in workshop_items if item_id.isdigit()]

    not_found_mod_ids = set(mod_ids)
    
    # Track duplicates
    duplicate_mod_ids = set()
    duplicate_workshop_items = set()

    # Process URLs
    for item_id in ids:
        url = f"{base_url}{item_id}"
        
        # Check for duplicate Workshop IDs
        if workshop_items.count(item_id) > 1:
            duplicate_workshop_items.add(item_id)
        
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
                
                # Track which Mod IDs have been reported for this URL
                reported_mod_ids = set()

                if page_mod_ids:
                    print(f"Mod IDs found on page: {page_mod_ids}")

                    for mod_id in mod_ids:
                        if mod_id in page_mod_ids:
                            if mod_id not in reported_mod_ids:
                                print(f"Matching Mod ID found in provided IDs: -> Mod ID: {mod_id}")
                                reported_mod_ids.add(mod_id)
                            if mod_id in not_found_mod_ids:
                                not_found_mod_ids.remove(mod_id)
                else:
                    print(f"Mod ID NOT FOUND: {url}")

        except Exception as e:
            print(f"Error: {url} -> {e}")

        print()  # Newline to separate different URLs

    # List any mod IDs not found
    if not_found_mod_ids:
        print("WARNING Mod IDs not found:")
        for mod_id in not_found_mod_ids:
            print(mod_id)

    # Check for duplicate Mod IDs in the provided list
    for mod_id in mod_ids:
        if mod_ids.count(mod_id) > 1:
            duplicate_mod_ids.add(mod_id)

    # Print duplicate warnings
    if duplicate_mod_ids:
        print("\nWARNING Duplicate Mod IDs Found:")
        for mod_id in duplicate_mod_ids:
            print(mod_id)

    if duplicate_workshop_items:
        print("\nWARNING Duplicate Workshop IDs Found in Provided Config:")
        for item_id in duplicate_workshop_items:
            print(item_id)
    
    # Note about duplicate entries
    print("\nNote: You should delete duplicate entries; they will cause configuration conflicts.")

if __name__ == "__main__":
    # Parse command-line arguments
    file_path = None
    if '-c' in sys.argv:
        try:
            file_path_index = sys.argv.index('-c') + 1
            file_path = sys.argv[file_path_index]
        except IndexError:
            print("Error: No file path provided after -c.")
            sys.exit(1)
    
    # Read workshop items and mod IDs from the specified file or current directory
    workshop_items, mod_ids = read_items_from_files(file_path)
    
    # Run the URL check
    check_urls(workshop_items, mod_ids)

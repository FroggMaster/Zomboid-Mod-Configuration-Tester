# Zomboid Mod Configuration Tester

## How to Use

1. **Prepare Your Config File:**
   - Copy your server configuration file (`.ini`) into the same directory as the script.
   - Rename the file from `.ini` to `.txt` (Note: The script will be updated in the future to support both `.txt` and `.ini` formats).

2. **Run the Script:**
   - Execute the script by running `python TestMods.py`.

## What the Script Does

- The script will locate the `.txt` file and extract all items from the `WorkshopItems=` and `Mods=` variables.
- It will then validate each item by:
  - Outputting the title of the page.
  - Listing any Mod IDs found on the page.
  - Confirming Mod IDs that match those in your configuration.
- Any pages that do not load a valid mod title will throw an error indicating they're not valid.
- Any Mod IDs in your configuration that cannot be found in valid mod URLs will be listed at the end of the script, with a notification indicating they were not located.

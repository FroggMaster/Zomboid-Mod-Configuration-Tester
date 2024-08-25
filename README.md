# Zomboid Mod Configuration Tester

## How to Use

1. **Prepare Your Config File:**
   - Copy your server configuration file (`.ini`) into the same directory as the script.

2. **Run the Script:**
      - Run the following command to install all the packages listed in requirements.txt:
     `pip install -r requirements.txt`
   - Execute the script by running `python TestMods.py`.

## What the Script Does

- The script will locate the `.txt` file and extract all items from the `WorkshopItems=` and `Mods=` variables.
- It will then validate each item by:
  - Outputting the title of the page.
  - Listing any Mod IDs found on the page.
  - Confirming Mod IDs that match those in your configuration.
- Any pages that do not load a valid mod title will throw an error indicating they're not valid.
- Any Mod IDs in your configuration that cannot be found in valid mod URLs will be listed at the end of the script, with a notification indicating they were not located.

### Example Output
<details>
  <summary>Click to expand</summary>

```
>python TestURLsAdvanced.py
Workshop items: ['2710167561', '2282429356', '1510950729', '2707957711']

Mod IDs: ['FakeModID', 'MapLegendUI', 'autotsartrailers', 'TrueActionsDancing']

Valid: https://steamcommunity.com/workshop/filedetails/?id=2710167561 -> Title: Steam Workshop::Map Legend UI
Mod IDs found on page: {'MapLegendUI'}
Matching Mod ID found in provided IDs: -> Mod ID: MapLegendUI

Valid: https://steamcommunity.com/workshop/filedetails/?id=2282429356 -> Title: Steam Workshop::Autotsar Trailers
Mod IDs found on page: {'autotsartrailers'}
Matching Mod ID found in provided IDs: -> Mod ID: autotsartrailers

Valid: https://steamcommunity.com/workshop/filedetails/?id=1510950729 -> Title: Steam Workshop::Filibuster Rhymes' Used Cars!
Mod IDs found on page: {'FRUsedCarsNRN'}

Valid: https://steamcommunity.com/workshop/filedetails/?id=2707957711 -> Title: Steam Workshop::True Actions. Act 3+. Dancing on VHS
Mod IDs found on page: {'TrueActionsDancing', 'TrueActionsDancingVHS_MAG'}
Matching Mod ID found in provided IDs: -> Mod ID: TrueActionsDancing

Mod IDs not found:
FakeModID
```
</details>

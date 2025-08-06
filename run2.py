# run.py

import os
import pandas as pd
from single_worker import scrape_group
from config import OUTPUT_FILE, GOOGLE_SHEET_NAME
from g_sheets_exporter import export_to_google_sheets

if __name__ == "__main__":
    ## >> NEW: Define your target number of results per chemical here.
    TARGET_RESULTS = 75  # Set this to 50, 75, 100, or whatever you need.
    
    os.makedirs("output", exist_ok=True)
    os.makedirs("errors", exist_ok=True)

    try:
        df_input = pd.read_csv("input_chemicals.csv")
        if "Chemical" not in df_input.columns:
            raise ValueError("Missing 'Chemical' column in input_chemicals.csv")
        chemicals = df_input["Chemical"].dropna().unique().tolist()
        print(f"🔢 Loaded {len(chemicals)} unique chemicals from input.")
        print(f"🎯 Target results per chemical: {TARGET_RESULTS}")
    except FileNotFoundError:
        print("❌ Failed to load input: 'input_chemicals.csv' not found.")
        exit()
    except Exception as e:
        print(f"❌ Failed to load input: {e}")
        exit()

    # --- Step 1: Scrape the data ---
    ## >> Pass the TARGET_RESULTS variable to the scraping function.
    results_list = scrape_group(chemicals, target_results_per_item=TARGET_RESULTS)

    if not results_list:
        print("\n⚠️ No results were scraped. Exiting.")
        exit()
        
    # --- Step 2: Convert to DataFrame ---
    results_df = pd.DataFrame(results_list)
    print(f"\n📊 Scraping complete. Total results: {len(results_df)}")

    # --- Step 3: Export to Google Sheets (Directly from DataFrame) ---
    try:
        export_to_google_sheets(results_df, GOOGLE_SHEET_NAME)
    except Exception as e:
        print(f" G-Sheet Export] -> ❌ An unexpected error occurred during export: {e}")
        
    # --- Step 4: Save a local backup CSV copy ---
    output_path = os.path.join("output", OUTPUT_FILE)
    results_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"💾 Local backup saved at: {output_path}")

    print("\n🎉 All tasks completed!")
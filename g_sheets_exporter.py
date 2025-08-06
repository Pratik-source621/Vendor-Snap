# g_sheets_exporter.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe, get_as_dataframe

## >> New 'mode' parameter allows you to choose between 'overwrite' and 'append'.
def export_to_google_sheets(df: pd.DataFrame, sheet_name: str, mode: str = 'append'):
    """
    Exports a pandas DataFrame to a specified Google Sheet.

    Args:
        df (pd.DataFrame): The DataFrame with new data to export.
        sheet_name (str): The name of the Google Spreadsheet.
        mode (str): 'overwrite' to replace all data, or 'append' to add new data.
    """
    if df.empty:
        print(" G-Sheet Export] -> ⚠️ DataFrame is empty. Nothing to export.")
        return

    print(f"\n G-Sheet Export] -> Mode: {mode.upper()}")
    print(" G-Sheet Export] -> Authenticating with Google...")
    try:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        print(" G-Sheet Export] -> Authentication successful.")
    except FileNotFoundError:
        print(" G-Sheet Export] -> ❌ Authentication Failed. 'credentials.json' not found.")
        return
    except Exception as e:
        print(f" G-Sheet Export] -> ❌ Authentication Failed. Error: {e}")
        return

    try:
        spreadsheet = client.open(sheet_name)
        
        try:
            worksheet = spreadsheet.worksheet("ScrapedData")
            print(f" G-Sheet Export] -> Found existing worksheet 'ScrapedData'.")
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="ScrapedData", rows="1000", cols="20")
            print(f" G-Sheet Export] -> Created new worksheet 'ScrapedData'.")

        ## >> NEW LOGIC FOR APPENDING DATA <<
        if mode == 'append':
            print(" G-Sheet Export] -> Reading existing data from sheet...")
            # Use get_as_dataframe to read the sheet into a DataFrame
            # The 'evaluate_formulas=True' can be useful if you have formulas in your sheet.
            try:
                # We ignore the header row from the sheet as pandas will add its own
                existing_df = get_as_dataframe(worksheet, evaluate_formulas=True)
                # Drop rows that are completely empty
                existing_df.dropna(how='all', inplace=True)
                print(f" G-Sheet Export] -> Found {len(existing_df)} existing rows.")
                
                # Use pandas.concat to join the old and new data
                final_df = pd.concat([existing_df, df], ignore_index=True)
                
                # Optional: Remove duplicate rows based on a key column, like 'Product Name' or 'Phone'
                # This prevents adding the same item multiple times if you re-scrape it.
                final_df.drop_duplicates(subset=['Product Name', 'Company', 'Phone'], keep='last', inplace=True)
                
                print(f" G-Sheet Export] -> Combined data has {len(final_df)} total unique rows.")

            except Exception as e:
                print(f" G-Sheet Export] -> Could not read existing data (sheet might be empty). Writing new data only. Error: {e}")
                final_df = df
        else: # Overwrite mode
            final_df = df
            print(f" G-Sheet Export] -> Overwrite mode selected. Sheet will be cleared.")

        # Write the final, combined DataFrame back to the sheet
        print(f" G-Sheet Export] -> Writing {len(final_df)} rows to the sheet...")
        set_with_dataframe(worksheet, final_df)
        
        print(f"✅ G-Sheet Export] -> Successfully updated Google Sheet!")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f" G-Sheet Export] -> ❌ Spreadsheet Not Found. Did you create a Google Sheet named '{sheet_name}' and share it with your service account email?")
    except Exception as e:
        print(f" G-Sheet Export] -> ❌ An error occurred during export: {e}")
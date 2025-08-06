# g_sheets_exporter.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe # ## >> Import the helper function

## >> The function now accepts a DataFrame directly, not a file path. This is more efficient.
def export_to_google_sheets(df: pd.DataFrame, sheet_name: str):
    """
    Exports a pandas DataFrame to a specified Google Sheet.
    """
    if df.empty:
        print(" G-Sheet Export] -> ⚠️ DataFrame is empty. Nothing to export.")
        return

    print("\n G-Sheet Export] -> Authenticating with Google...")
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

        # ## >> This is the magic! set_with_dataframe is much cleaner and more robust.
        # It handles clearing the sheet and writing the header and data in one step.
        print(f" G-Sheet Export] -> Clearing sheet and writing {len(df)} new rows...")
        set_with_dataframe(worksheet, df)
        
        print(f"✅ G-Sheet Export] -> Successfully exported {len(df)} rows to Google Sheets!")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f" G-Sheet Export] -> ❌ Spreadsheet Not Found. Did you create a Google Sheet named '{sheet_name}' and share it with your service account email?")
    except Exception as e:
        print(f" G-Sheet Export] -> ❌ An error occurred during export: {e}")
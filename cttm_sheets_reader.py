import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- CONFIGURATION ---
# This is the unique URL of your CTTM Ground Truth Ledger Google Sheet
# You must update this variable after you create your sheet.
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit" 
# NOTE: The sheet name is usually "Sheet1" by default, or the name of the sheet 
# where your Google Form sends its responses.
SHEET_NAME = "Form Responses 1" 

# --- CTTM-J READING FUNCTION ---

@st.cache_data(ttl=datetime.timedelta(minutes=5))
def load_junos_intelligence():
    """
    Connects to the secure CTTM Ground Truth Ledger via Google Sheets 
    and filters for the 'Actionable Intelligence' layer (Junos Push).
    
    This function requires the GCP Service Account credentials to be set 
    in Streamlit Secrets under the 'gsheets' connection name.
    """
    try:
        # 1. Establish Secure Connection
        # Streamlit automatically uses the secrets configured for 'gsheets'
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 2. Read the Raw Data from the Form Responses Sheet
        # The 'usecols' ensures we only fetch the columns we need for CTTM-J
        data = conn.read(
            spreadsheet=SHEET_URL,
            worksheet=SHEET_NAME,
            usecols=[0, 1, 2, 3] # Assuming Timestamp, Report, Confidence, Junos Tag
        )
        
        # 3. Clean and Rename Columns (MUST MATCH YOUR GOOGLE FORM ORDER!)
        # The column names are what the Google Form creates. You must confirm these.
        data.columns = [
            'Timestamp', 
            'Intelligence_Report', 
            'Confidence_Level', 
            'Junos_Tag' # This should be True/False based on the form checkbox
        ]
        
        # 4. Filter for Junos Insight Criteria (Paññā Logic)
        # Filters for high-priority unconfirmed news (Junos_Tag = True)
        # And data where confidence is not 100% (based on your dropdown structure)
        junos_intelligence = data[
            (data['Junos_Tag'] == True) & 
            (~data['Confidence_Level'].str.contains("100%", na=False))
        ].copy() # Use .copy() to avoid SettingWithCopyWarning
        
        # 5. Format Output for RAG Injection
        # We convert the DataFrame rows into a list of strings for the Gemini RAG prompt
        junos_list = []
        for index, row in junos_intelligence.iterrows():
            confidence_score = row['Confidence_Level'].split(' ')[0] # Extract the percentage
            report = f"[{row['Timestamp']}] [INTELLIGENCE: {confidence_score} CONFIDENCE] {row['Intelligence_Report']}"
            junos_list.append(report)
            
        return "\n".join(junos_list)

    except Exception as e:
        # Returns an error message that the main app can handle
        return f"🚨 CTTM-J Data Error: Could not load Junos Insight. Check Google Sheets connection and secrets. Error: {e}"

# Example of how to use this in your dhammi_chat function:
# junos_context = load_junos_intelligence() 
# Inject junos_context into your Gemini prompt for the CTTM-J capability.

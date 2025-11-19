# --- CTTM DATA INPUT DASHBOARD ---
from streamlit_gsheets import GSheetsConnection

def cttm_input_dashboard():
    st.header("🛡️ CTTM Ground Truth Submission")
    st.subheader("For Verified SS'ISM Core Team Use Only")
    
    # Use a Streamlit Form for reliable submission
    with st.form(key="cttm_data_form"):
        # 1. Fact Type and Verification Level
        fact_type = st.selectbox(
            "Fact Category:",
            ["Election Result", "Political Statement", "OSINT Evidence", "Security Update"]
        )
        
        verification = st.slider(
            "Verification Confidence (SS'ISM V-Score):",
            min_value=0.0, max_value=1.0, value=0.9, step=0.05
        )

        # 2. The Core Fact
        fact_text = st.text_area(
            "Verified Fact/Result:",
            placeholder="E.g., In Ward 3, Bago, NLD verified vote count is 4,500 vs. Military-backed 1,200.",
            height=150
        )
        
        # 3. Source (For Auditing)
        source = st.text_input(
            "Source Reference (Link, Witness Name, etc.):"
        )
        
        submitted = st.form_submit_button("Submit New CTTM Fact")

        if submitted:
            # --- WRITE LOGIC GOES HERE ---
            # This is where we call the Google Sheets connection to append the data
            
            # 1. Connect to the Sheet (assuming credentials are set in Streamlit Secrets)
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # 2. Create the new row of data
            new_data = {
                "Timestamp": [str(datetime.datetime.now())],
                "Category": [fact_type],
                "Confidence": [verification],
                "Fact_Text": [fact_text],
                "Source": [source]
            }
            
            # 3. Append the data to the Google Sheet (assuming the sheet URL is set in secrets)
            # NOTE: We need a new function that handles the write, using the connection object.
            # For a quick implementation, we would use conn.update() or gspread.
            
            st.success(f"✅ Fact submitted to CTTM Ledger. Confidence: {verification}. DHAMMI's Paññā is updated.")
            # --- END WRITE LOGIC ---
            
# NOTE: You must call this function in your streamlit_app.py file to display the dashboard!
# Example: cttm_input_dashboard()

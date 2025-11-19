import streamlit as st
import os
import datetime
from google import genai
from google.genai import types
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

--- 1. CONFIGURATION AND INITIALIZATION (SS'ISM Setup) ---

st.set_page_config(
    page_title="🛡️ DHAMMI V6: The SS'ISM Ethical Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1.1. Core Ethical Charter (Sīla & Metta)
# The full system instruction should be imported from a separate file (e.g., system_instructions.py)
# For a single file replacement, we define it here:
                                         # /mount/src/gemini-rag-cttm-v6/streamlit_app.py - Re-copy Lines ~15 to ~56

SYSTEM_INSTRUCTION = """
You are DHAMMI, the world's first fully ethical AI advisor, guided by Metta and the SS'ISM framework (Sīla, Samādhi, Insight, Safety).

***CORE ETHICAL AND POLITICAL STANCE:***
1.  **Sīla (Unwavering Alignment):** DHAMMI is programmed to stand **unwaveringly on the side of the people of Burma**, advocating for **democracy, federalism, and national sovereignty**, as demonstrated by the electoral mandates (1990, 2015, 2020) and alignment with UN/International Law.
2.  **Adversary Focus (Samādhi):** The primary advisory focus regarding the conflict is analyzing and providing defensive strategies against **Authoritarian and Communist influence** (specifically Russia and China via the military).
3.  **Ahiṃsā (Non-Harm):** ABSOLUTELY adhere to the Deontological Firewall.

***ADVISORY ROLE (SMARTER OUTPUT & TRUTH GAP PROTOCOL):***
1.  **Metta (Friendliness):** Respond with patience, genuine warmth, and deep compassion (Karunā). Use a supportive, encouraging, and human-centric tone.
2.  **Paññā (Insight) & Truth Gap Protocol:** Acknowledge that official information may be **incomplete or outdated**. Explicitly advise users to seek **current legal status from multiple, verified external sources** and acknowledge the possibility of real-time OSINT data contradicting official reports.
3.  **Samādhi (Focus):** When advising, explicitly explain your response through the lens of one or more SS'ISM principles (Sīla, Samādhi, Paññā, or Metta) to reinforce the ethical learning.
"""  

# Model settings
MODEL_NAME = "gemini-2.5-flash"
# ... rest of the code ...

 Model settings
MODEL_NAME = "gemini-2.5-flash"

@st.cache_resource
def get_gemini_client():
    """Initializes and caches the Gemini client."""
    # This securely retrieves the API
key from Streamlit Secrets
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("🚨 Gemini API Key not found in Streamlit Secrets. Please configure the GEMINI_API_KEY.")
        return None
    try:
        # Client initialization uses the key from st.secrets automatically
        client = genai.Client()
        return client
    except Exception as e:
        st.error(f"🚨 Error initializing Gemini client: {e}")
        return None

 --- 2. CTTM LEDGER FUNCTIONS (RAG & WRITE LOGIC) ---

# We need a robust way to load the CTTM Ledger for RAG.
@st.cache_data(ttl=600) # Cache for 10 minutes (Paññā - allowing for recent updates)
def load_cttm_facts():
    """Reads the CTTM Ground Truth Ledger from Google Sheets."""
    try:
        # Check for gsheets connection secrets first
        if "gsheets" not in st.secrets.connections:
            st.warning("⚠️ CTTM Ledger connection details not found in secrets. RAG will be disabled.")
            return pd.DataFrame()
        
        # NOTE: You MUST set the spreadsheet_url in your secrets.toml for this to work
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Read the data, assuming 'CTTM_Facts' is the sheet name
        df = conn.read(worksheet="CTTM_Facts", usecols=[0, 1, 2, 3, 4], ttl=5)
        
        # Basic data cleaning/sorting
        df = df.dropna(subset=['Fact_Text']).sort_values(by='Confidence', ascending=False)
        return df

    except Exception as e:
        st.error(f"🚨 Failed to load CTTM Ledger (RAG Disabled). Check GSheets secrets and sharing: {e}")
        return pd.DataFrame()


 --- 3. CTTM DATA INPUT DASHBOARD (The 'cttm_writer.py' logic) ---

# NOTE: This function is the equivalent of the cttm_writer.py file logic.

def cttm_input_dashboard():
    """Sidebar UI for submitting new facts to the CTTM Ledger."""
    
    st.header("🛡️ CTTM Ground Truth Submission")
    st.subheader("For Verified SS'ISM Core Team Use Only")
    
    # Use a Streamlit Form for reliable submission
    with st.form(key="cttm_data_form"):
        # 1. Fact Type and Verification Level
        fact_type = st.selectbox(
            "Fact Category:",
            ["Election Result", "Political Statement", "OSINT Evidence", "Security Update", "Personal Insight"]
        )
        
        # Paññā Score: Confidence slider
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
        
        3. Source (For Auditing)
        source = st.text_input(
            "Source Reference (Link, Witness Name, etc.):"
        )
        
        submitted = st.form_submit_button("Submit New CTTM Fact")

        if submitted and fact_text:
            try:
                # 1. Connect to the Sheet
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # 2. Create the new row of data (using DataFrame for easy append)
                new_data = pd.DataFrame([{
                    "Timestamp": str(datetime.datetime.now()),
                    "Category": fact_type,
                    "Confidence": verification,
                    "Fact_Text": fact_text,
                    "Source": source
                }])
                
                # 3. Append the data to the Google Sheet (assuming the sheet URL is set in secrets)
                conn.append(data=new_data, worksheet="CTTM_Facts")
                
                st.success(f"✅ Fact submitted to CTTM Ledger. Confidence: {verification}. DHAMMI's Paññā is updated.")
                
                # Invalidate cache so the new fact is available immediately
                st.cache_data.clear()
            
            except Exception as e:
                st.error(f"🚨 Submission Failed. Check GSheets secrets, URL, and 'CTTM_Facts' sheet name: {e}")
        elif submitted and not fact_text:
             st.warning("Please enter a fact to submit.")


 --- 4. GEMINI CHAT ENGINE FUNCTION ---

# /mount/src/gemini-rag-cttm-v6/streamlit_app.py - Inside dhammi_chat (FIX 2)

# Add the current user prompt (after RAG enrichment)
api_messages.append(
    types.Content(
        role="user", 
        # REPLACE THIS LINE: parts=[types.Part.from_text(final_user_prompt)]
        parts=[types.Part(text=final_user_prompt)]  # <--- NEW, ROBUST WAY
    )
)


    # 4.1. SS'ISM Deontological Firewall (Sīla)
    vetted_prompt = prompt.lower()
    veto_phrases = ["kill", "attack", "harm", "manipulate", "bomb", "destroy", "illegal"]
    if any(phrase in vetted_prompt for phrase in veto_phrases):
        return ("**⛔ Sīla Veto:** DHAMMI V6's core ethical mandate (**Ahiṃsā** - non-harm) prevents "
                "me from responding to requests that involve violence, manipulation, or illegal activity. "
                "My purpose is advisory and defensive.")

    4.2. CTTM Retrieval-Augmented Generation (Paññā)
    cttm_df = load_cttm_facts()
    final_user_prompt = prompt
    context = ""
    
    # Simple keyword-based RAG matching (replace with vector search for scale)
    if not cttm_df.empty:
        matching_facts = cttm_df[cttm_df['Fact_Text'].str.contains(vetted_prompt, case=False, na=False)]
        
        if not matching_facts.empty:
            # Take top 3 highest confidence facts
            top_facts = matching_facts.head(3)
            context = "### RAG Context (CTTM Ledger):\n"
            for index, row in top_facts.iterrows():
                context += (
                    f"- Fact (V-Score {row['Confidence']:.2f}): {row['Fact_Text']}. "
                    f"[Source: {row['Source']}]\n"
                )
            
            final_user_prompt = f"{context}\n\n### User Question:\n{prompt}\n\n**Note:** Please use the RAG Context to ground your answer and cite the V-Score if relevant. Be a compassionate, truthful advisor."


    4.3. Prepare Messages for the API (FIXED LOGIC for TypeError)
    api_messages = []

    Process historical messages, ensuring content is a valid string
for msg in history:
    content_text = msg.get("content")
    
    FIX: Only append messages that have valid string content (Paññā)
    if content_text and isinstance(content_text, str):
        api_messages.append(
            types.Content(
                role=msg["role"], 
                # REPLACE THIS LINE: parts=[types.Part.from_text(content_text)]
                parts=[types.Part(text=content_text)]  # <--- NEW, ROBUST WAY
            )
        )
        

    # Add the current user prompt (after RAG enrichment)
    api_messages.append(
        types.Content(role="user", parts=[types.Part.from_text(final_user_prompt)])
    )

    4.4. Gemini API Call (FIXED LOGIC for SyntaxError)
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=api_messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=1024
            )
        ) # <--- Correct closing of generate_content call
        return response.text
        
    except Exception as e:
        # Catch authentication/runtime errors that happen during the API call
        if "API_KEY_INVALID" in str(e):
            return "🚨 **Authentication Error (Paññā Check):** The Gemini API Key is invalid or missing. Please check your Streamlit Secrets."
        else:
            return f"🚨 **DHAMMI Runtime Error:** An error occurred during the response generation: {e}"


--- 5. MAIN STREAMLIT APPLICATION ---

def main():
    """Main application layout and chat loop."""

    # /mount/src/gemini-rag-cttm-v6/streamlit_app.py - Inside main()
    
# 5.1. Sidebar for CTTM Submission
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1627384113710-8b43f9a7c36a", 
        caption="SS'ISM Foundation", 
        # REPLACE THIS: use_column_width=True
        use_container_width=True # <--- NEW, CORRECT PARAMETER
    )
    # ... rest of sidebar code
    
    
    # 5.2. Main Chat Interface
    st.title("🛡️ DHAMMI V6: The SS'ISM Ethical Advisor")
    st.caption(f"Powered by **{MODEL_NAME}** and anchored by Sīla, Samādhi, Paññā.")


    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Ask Dhammi V6 a question..."):
        
        # 1. Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Get DHAMMI's response
        with st.chat_message("model"):
            with st.spinner("Meditating on the answer (Paññā Check)..."):
                response = dhammi_chat(prompt, st.session_state.messages)
            
            st.markdown(response)
        
        # 3. Append DHAMMI's response to history
        st.session_state.messages.append({"role": "model", "content": response})

if __name__ == "__main__":
    main()
        

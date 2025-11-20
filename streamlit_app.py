import streamlit as st
import datetime
from google import genai
from google.genai import types
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import base64

# -------------------------
# 1. CONFIGURATION AND INITIALIZATION (SS'ISM Setup)
# -------------------------

st.set_page_config(
    page_title="🛡️ SS'ISM DHAMMI V6: The Ethical Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS FOR DESIGN (Vibrant Colors, Centering, Motto Color) ---
# NOTE: You MUST create an 'assets' folder in your GitHub repo and place the logo image inside it.
def local_css(file_name):
    """Function to load custom CSS from a file."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # If CSS file is missing, inject simple style for motto color
        st.markdown(f"""
            <style>
                /* Set Motto Text Color to a vibrant Cyan */
                .stApp [data-testid="stHeader"] h2 {{
                    color: #00FFFF; /* Cyan */
                    text-align: center;
                    font-size: 2.2em;
                    font-weight: 800;
                }}
                /* Ensure Title/Motto is readable */
                .stApp .css-1d3w5oq, .stApp .css-1gh1zsk {{
                    text-align: center;
                }}
            </style>
            """, unsafe_allow_html=True)

# Function to load local image as base64 for use in HTML/CSS (if needed for background, but simplified here)
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return ""


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

MODEL_NAME = "gemini-2.5-flash"

@st.cache_resource
def get_gemini_client():
    """Initializes and caches the Gemini client."""
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("🚨 Gemini API Key not found. Please add GEMINI_API_KEY to Streamlit Secrets.")
        return None
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"🚨 Error initializing Gemini client: {e}")
        return None

# -------------------------
# 2. CTTM LEDGER FUNCTIONS (RAG & WRITE LOGIC)
# -------------------------

@st.cache_data(ttl=600)
def load_cttm_facts():
    """Reads the CTTM Ground Truth Ledger from Google Sheets."""
    try:
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            return pd.DataFrame()
            
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="CTTM_Facts", usecols=[0, 1, 2, 3, 4], ttl=5)
        if df is None or df.empty:
            return pd.DataFrame()
        if "Fact_Text" not in df.columns:
            return pd.DataFrame()
        df = df.dropna(subset=['Fact_Text'])
        if "Confidence" in df.columns:
            df['Confidence'] = pd.to_numeric(df['Confidence'], errors='coerce').fillna(0.0)
        else:
            df['Confidence'] = 0.0
        df = df.sort_values(by='Confidence', ascending=False)
        return df
    except Exception as e:
        print(f"RAG Warning: {e}") 
        return pd.DataFrame()

# -------------------------
# 3. CTTM DATA INPUT DASHBOARD
# -------------------------

def cttm_input_dashboard():
    """Sidebar UI for submitting new facts."""
    st.header("🛡️ CTTM Ground Truth Submission")
    st.subheader("For Verified SS'ISM Core Team Use Only")

    with st.form(key="cttm_data_form"):
        fact_type = st.selectbox(
            "Fact Category:",
            ["Election Result", "Political Statement", "OSINT Evidence", "Security Update", "Personal Insight"]
        )
        verification = st.slider(
            "Verification Confidence (SS'ISM V-Score):",
            min_value=0.0, max_value=1.0, value=0.9, step=0.05
        )
        fact_text = st.text_area(
            "Verified Fact/Result:",
            placeholder="E.g., In Ward 3, Bago, NLD verified vote count is 4,500 vs. Military-backed 1,200.",
            height=150
        )
        source = st.text_input("Source Reference (Link, Witness Name, etc.):")
        submitted = st.form_submit_button("Submit New CTTM Fact")

        if submitted:
            if not fact_text:
                st.warning("Please enter a fact to submit.")
            else:
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    new_data = pd.DataFrame([{
                        "Timestamp": str(datetime.datetime.now()),
                        "Category": fact_type,
                        "Confidence": verification,
                        "Fact_Text": fact_text,
                        "Source": source
                    }])
                    conn.append(data=new_data, worksheet="CTTM_Facts")
                    st.success(f"✅ Fact submitted to CTTM Ledger. Confidence: {verification}.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"🚨 Submission Failed. Check GSheets secrets: {e}")

# -------------------------
# 4. GEMINI CHAT ENGINE (dhammi_chat)
# -------------------------

def dhammi_chat(prompt: str, history: list):
    """Generate a response using CTTM RAG and the Gemini client."""
    client = get_gemini_client()
    if client is None:
        return "🚨 Gemini client not configured."

    # 4.1 Deontological Firewall (Sīla)
    vetted_prompt = prompt.lower()
    veto_phrases = ["kill", "attack", "harm", "manipulate", "bomb", "destroy", "illegal"]
    if any(phrase in vetted_prompt for phrase in veto_phrases):
        return ("**⛔ Sīla Veto:** DHAMMI V6's core ethical mandate (**Ahiṃsā**) prevents "
                "me from responding to requests that involve violence or illegal activity.")

    # 4.2 RAG (Paññā)
    cttm_df = load_cttm_facts()
    final_user_prompt = prompt
    
    if not cttm_df.empty:
        tokens = re.findall(r"\w{3,}", prompt)
        pattern = "|".join(re.escape(t) for t in tokens[:12])
        if pattern:
            matching_facts = cttm_df[cttm_df['Fact_Text'].str.contains(pattern, case=False, na=False, regex=True)]
            if not matching_facts.empty:
                top_facts = matching_facts.head(3)
                context_lines = []
                for _, row in top_facts.iterrows():
                    vscore = row.get('Confidence', 0.0)
                    fact_text = row.get('Fact_Text', '')
                    context_lines.append(f"- Fact (V-Score {vscore:.2f}): {fact_text}")
                context = "### RAG Context (CTTM Ledger):\n" + "\n".join(context_lines) + "\n"
                final_user_prompt = f"{context}\n\n### User Question:\n{prompt}\n\n(Use the RAG Context if relevant)"

    # 4.3 Prepare messages
    api_messages = []
    messages_to_process = history[:-1] if history and history[-1]["role"] == "user" else history

    for msg in messages_to_process:
        role = msg["role"]
        content = msg["content"]
        # MAP ROLES: Streamlit "assistant" -> Gemini "model"
        if role == "assistant":
            api_role = "model"
        else:
            api_role = "user"
        api_messages.append(types.Content(role=api_role, parts=[types.Part(text=content)]))

    api_messages.append(types.Content(role="user", parts=[types.Part(text=final_user_prompt)]))

    # 4.4 Call Gemini - UNLOCKED VERSION
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=api_messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                # INCREASED TOKEN LIMIT to prevent cutoff
                max_output_tokens=8192, 
                # ADJUSTED SAFETY SETTINGS to allow political discourse
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_ONLY_HIGH"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_ONLY_HIGH"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_ONLY_HIGH"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_ONLY_HIGH"
                    ),
                ]
            )
        )
        return response.text
    except Exception as e:
        return f"🚨 **DHAMMI Runtime Error:** {e}"

# -------------------------
# 5. MAIN STREAMLIT APPLICATION
# -------------------------

def main():
    # --- 5.1 Load Custom CSS for Styling ---
    # Attempt to load style.css (best practice for complex styling)
    local_css("./assets/style.css") 
    
    # --- 5.2 Sidebar (CTTM Dashboard) ---
    with st.sidebar:
        # Placeholder for sidebar logo. You can replace this with a more suitable 'SS'ISM' logo.
        st.image(
            "https://images.unsplash.com/photo-1627384113710-8b43f9a7c36a",
            caption="SS'ISM Foundation",
            use_container_width=True
        )
        cttm_input_dashboard()

    # --- 5.3 NEW MAIN PAGE HEADER (The Poormanmeism Core Design) ---
    
    # 5.3.1 Google Branding (Top of the App)
    st.markdown(f'<div style="text-align: center; margin-bottom: 5px;">'
                f'<img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png" alt="Google Logo" style="height: 30px;"/>'
                f'<br>Powered by <span style="font-weight: bold; color: #4285F4;">Google</span> <span style="font-weight: bold; color: #34A853;">Gemini</span>'
                f'</div>', unsafe_allow_html=True)
    
    # 5.3.2 SS'ISM V6 Logo (Must be uploaded to GitHub in the 'assets' folder)
    # Using a placeholder image for now. Upload your dhammi_logo_v6.png to 'assets/'
    logo_path = "./assets/dhammi_logo_v6.png" 
    st.image(logo_path, use_column_width=False, width=150)

    # 5.3.3 Main Title (SS'ISM DHAMMI V6)
    st.markdown('<h1 style="text-align: center; color: #FFD700;">🛡️ SS\'ISM DHAMMI V6: The Ethical Advisor</h1>', unsafe_allow_html=True)

    # 5.3.4 Motto (The centerpiece, styled with custom CSS)
    st.markdown('<h2>CODE WITH TRUTH. DEFEAT PSY-WAR.</h2>', unsafe_allow_html=True)

    # 5.3.5 Philosophy (The supporting text)
    st.markdown(f'<div style="text-align: center; margin-bottom: 30px; font-style: italic; color: #CCCCCC;">'
                f'The more you feed truth, the less space there is for disinformation. '
                f'We fight information wars with transparency.'
                f'</div>', unsafe_allow_html=True)

    # Horizontal Divider for a clean separation from the chat area
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user prompt
    if prompt := st.chat_input("Ask DHAMMI V6 a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Meditating on the answer (Paññā Check)..."):
                response = dhammi_chat(prompt, st.session_state.messages)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
        

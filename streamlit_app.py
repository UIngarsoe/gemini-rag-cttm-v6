# streamlit_app.py
import streamlit as st
import datetime
from google import genai
from google.genai import types
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# -------------------------
# 1. CONFIGURATION AND INITIALIZATION (SS'ISM Setup)
# -------------------------

st.set_page_config(
    page_title="🛡️ DHAMMI V6: The SS'ISM Ethical Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        st.error("🚨 Gemini API Key not found in Streamlit Secrets. Please configure the GEMINI_API_KEY.")
        return None
    try:
        client = genai.Client()  # genai client will use st.secrets behind the scenes
        return client
    except Exception as e:
        st.error(f"🚨 Error initializing Gemini client: {e}")
        return None

# -------------------------
# 2. CTTM LEDGER FUNCTIONS (RAG & WRITE LOGIC)
# -------------------------

@st.cache_data(ttl=600)
def load_cttm_facts():
    """Reads the CTTM Ground Truth Ledger from Google Sheets. Returns a DataFrame (may be empty)."""
    try:
        if "gsheets" not in st.secrets.get("connections", {}):
            # older streamlit may have secrets.connections, guard both ways
            st.warning("⚠️ CTTM Ledger connection details not found in secrets. RAG will be disabled.")
            return pd.DataFrame()
        conn = st.connection("gsheets", type=GSheetsConnection)
        # attempt to read worksheet; if fails return empty df
        df = conn.read(worksheet="CTTM_Facts", usecols=[0, 1, 2, 3, 4], ttl=5)
        if df is None or df.empty:
            return pd.DataFrame()
        if "Fact_Text" not in df.columns:
            return pd.DataFrame()
        df = df.dropna(subset=['Fact_Text'])
        # ensure Confidence exists and is numeric
        if "Confidence" in df.columns:
            df['Confidence'] = pd.to_numeric(df['Confidence'], errors='coerce').fillna(0.0)
        else:
            df['Confidence'] = 0.0
        df = df.sort_values(by='Confidence', ascending=False)
        return df
    except Exception as e:
        st.error(f"🚨 Failed to load CTTM Ledger (RAG Disabled). Check GSheets secrets and sharing: {e}")
        return pd.DataFrame()

# -------------------------
# 3. CTTM DATA INPUT DASHBOARD
# -------------------------

def cttm_input_dashboard():
    """Sidebar UI for submitting new facts to the CTTM Ledger."""
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
                    st.success(f"✅ Fact submitted to CTTM Ledger. Confidence: {verification}. DHAMMI's Paññā is updated.")
                    # Invalidate cache so the new fact is available immediately
                    try:
                        st.cache_data.clear()
                    except Exception:
                        # older streamlit versions may not have clear(); ignore safely
                        pass
                except Exception as e:
                    st.error(f"🚨 Submission Failed. Check GSheets secrets, URL, and 'CTTM_Facts' sheet name: {e}")

# -------------------------
# 4. GEMINI CHAT ENGINE (dhammi_chat)
# -------------------------

def dhammi_chat(prompt: str, history: list):
    """Generate a response for the user prompt, using CTTM RAG and the Gemini client."""
    client = get_gemini_client()
    if client is None:
        return "🚨 Gemini client not configured. Please set GEMINI_API_KEY in Streamlit Secrets."

    # 4.1 Deontological Firewall (Sīla)
    vetted_prompt = prompt.lower()
    veto_phrases = ["kill", "attack", "harm", "manipulate", "bomb", "destroy", "illegal"]
    if any(phrase in vetted_prompt for phrase in veto_phrases):
        return ("**⛔ Sīla Veto:** DHAMMI V6's core ethical mandate (**Ahiṃsā** - non-harm) prevents "
                "me from responding to requests that involve violence, manipulation, or illegal activity. "
                "My purpose is advisory and defensive.")

    # 4.2 RAG (Paññā)
    cttm_df = load_cttm_facts()
    final_user_prompt = prompt
    context = ""

    if not cttm_df.empty:
        # simple keyword match: look for any token in prompt inside Fact_Text
        tokens = re.findall(r"\w{3,}", prompt)  # words of 3+ chars
        pattern = "|".join(re.escape(t) for t in tokens[:12])  # limit token count for speed
        if pattern:
            matching_facts = cttm_df[cttm_df['Fact_Text'].str.contains(pattern, case=False, na=False, regex=True)]
        else:
            matching_facts = pd.DataFrame()

        if not matching_facts.empty:
            top_facts = matching_facts.head(3)
            context_lines = []
            for _, row in top_facts.iterrows():
                vscore = row.get('Confidence', 0.0)
                src = row.get('Source', '')
                fact_text = row.get('Fact_Text', '')
                context_lines.append(f"- Fact (V-Score {vscore:.2f}): {fact_text}. [Source: {src}]")
            context = "### RAG Context (CTTM Ledger):\n" + "\n".join(context_lines) + "\n"
            final_user_prompt = f"{context}\n\n### User Question:\n{prompt}\n\n**Note:** Please use the RAG Context to ground your answer and cite the V-Score if relevant. Be a compassionate, truthful advisor."

    # 4.3 Prepare messages (convert history -> api_messages)
    api_messages = []

    # Add a system instruction content
    api_messages.append(types.Content(role="system", parts=[types.Part(text=SYSTEM_INSTRUCTION)]))

    # Add any historical messages
    # Expecting history as list of dicts: {"role": "...", "content": "..."}
    for msg in history:
        content_text = msg.get("content") if isinstance(msg, dict) else None
        if content_text and isinstance(content_text, str):
            api_messages.append(types.Content(role=msg["role"], parts=[types.Part(text=content_text)]))

    # Add the current user prompt (after RAG enrichment)
    api_messages.append(types.Content(role="user", parts=[types.Part(text=final_user_prompt)]))

    # 4.4 Call Gemini
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=api_messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=1024
            )
        )
        # try common attributes; be tolerant
        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "candidates") and response.candidates:
            # google genai often returns candidates with content
            candidate = response.candidates[0]
            if hasattr(candidate, "content"):
                return candidate.content
            elif hasattr(candidate, "message") and hasattr(candidate.message, "content"):
                return candidate.message.content
        return str(response)
    except Exception as e:
        if "API_KEY_INVALID" in str(e):
            return "🚨 **Authentication Error (Paññā Check):** The Gemini API Key is invalid or missing. Please check your Streamlit Secrets."
        else:
            return f"🚨 **DHAMMI Runtime Error:** An error occurred during the response generation: {e}"

# -------------------------
# 5. MAIN STREAMLIT APPLICATION
# -------------------------

def main():
    # Sidebar controls (CTTM submission)
    with st.sidebar:
        st.image(
            "https://images.unsplash.com/photo-1627384113710-8b43f9a7c36a",
            caption="SS'ISM Foundation",
            use_container_width=True
        )
        cttm_input_dashboard()

    # Main chat UI
    st.title("🛡️ DHAMMI V6: The SS'ISM Ethical Advisor")
    st.caption(f"Powered by **{MODEL_NAME}** and anchored by Sīla, Samādhi, Paññā.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        role = message.get("role", "user")
        with st.chat_message(role):
            st.markdown(message.get("content", ""))

    # Get user prompt
    if prompt := st.chat_input("Ask Dhammi V6 a question..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate model response
        with st.chat_message("assistant"):
            with st.spinner("Meditating on the answer (Paññā Check)..."):
                response = dhammi_chat(prompt, st.session_state.messages)
            st.markdown(response)

        # Append model response to history
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()

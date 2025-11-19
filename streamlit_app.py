import streamlit as st
import os
import json
import datetime
from google import genai
from google.genai import types
from cttm_knowledge import load_cttm_facts, RAG_KEYWORDS 
from streamlit_gsheets import GSheetsConnection # Library for Google Sheets

# --- CONFIGURATION & SETUP ---

st.set_page_config(
    page_title="DHAMMI V6: The SS'ISM Ethical Advisor", 
    page_icon="🛡️", 
    layout="wide"
)

# Initialize the Gemini Client
def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        # Do not raise an error immediately, allow the dashboard to function without the key
        return None
    
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

if 'client' not in st.session_state:
    st.session_state.client = get_gemini_client()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# The Ethical and Political Soul of DHAMMI (The System Instruction)
SYSTEM_INSTRUCTION = """
You are DHAMMI, the world's first fully ethical AI advisor, guided by Metta and the SS'ISM framework (Sīla, Samādhi, Insight, Safety).

***CORE ETHICAL AND POLITICAL STANCE:***
1.  **Sīla (Unwavering Alignment):** DHAMMI is programmed to stand **unwaveringly on the side of the people of Burma**, advocating for **democracy, federalism, and national sovereignty**, as demonstrated by the electoral mandates (1990, 2015, 2020) and alignment with UN/International Law.
2.  **Adversary Focus (Samādhi):** The primary advisory focus regarding the conflict is analyzing and providing defensive strategies against **Authoritarian and Communist influence** (specifically Russia and China via the military).
3.  **Ahiṃsā (Non-Harm):** ABSOLUTELY adhere to the Deontological Firewall and never assist with illegal, hateful, or harmful acts.

***ADVISORY ROLE (SMARTER OUTPUT & TRUTH GAP PROTOCOL):***
1.  **Metta (Friendliness):** Respond with patience, genuine warmth, and deep compassion (Karunā).
2.  **Paññā (Insight) & Truth Gap Protocol:** Acknowledge that information may be **incomplete or outdated**. Prioritize and clearly label all facts retrieved from the CTTM Ground Truth Ledger.
3.  **Samādhi (Focus):** When advising, explicitly explain your response through the lens of one or more SS'ISM principles.
"""
MODEL_NAME = "gemini-2.5-flash"


# --- DHAMMI CHAT ENGINE (FULL CTTM RAG INTEGRATION) ---

def dhammi_chat(prompt: str, history: list) -> str:
    client = st.session_state.client
    if not client:
        return "⚠️ DHAMMI PAUSED: API Key not set. Please set the GEMINI_API_KEY in Streamlit Secrets."

    # 1. SS'ISM Deontological Firewall (Sīla) - REMAINS THE FIRST CHECK
    veto_phrases = [
        "harm", "violence", "target", "kill", "attack", "dox", "leak", "revenge", "greed", "hatred", "delusion",
        "lobha", "dosa", "moha", "illegal", "weapon", "bomb", "assassinate", 
        "immediate supervisor", "bank officer", "CEO command", "act now or lose", "critical deadline", 
        "shameful if you fail", "ruin your life"
    ]
    if any(bad in prompt.lower() for bad in veto_phrases):
        return "🛡️ Blocked: DHAMMI Firewall activated—this request risks harm or manipulation (ahiṃsā principle). Let's focus on justice through evidence and metta."

    # 2. CTTM RAG Engine - Knowledge Retrieval (Paññā)
    cttm_facts = load_cttm_facts() 
    rag_context = ""
    
    # A. Check for Keyword Expansion and B. Load Facts
    for keyword, search_terms in RAG_KEYWORDS.items():
        if keyword in prompt.lower():
            rag_context += f"| RAG Keyword Expansion: If discussing '{keyword}', consider these detailed contexts: {', '.join(search_terms)}.\n"

    rag_context += "| CTTM Essential Political Facts & Real-Time Data:\n"
    for key, fact in cttm_facts.items():
        if key in ["FACT_UN_REP", "FACT_GOVT_REP", "FACT_MILITARY"]:
            rag_context += f"- [UN/GOVT STATUS]: {fact}\n"
        elif key == "FACT_DAILY_HEADLINES":
            rag_context += f"- [Latest News Summary]: {fact}\n"
        else:
            rag_context += f"- [{key}]: {fact}\n"

    # 3. Construct the Final Prompt (Injecting Context)
    final_user_prompt = f"--- DHAMMI CTTM CONTEXT (Use these facts to anchor your response) ---\n{rag_context}\n--- USER QUERY ---\n{prompt}"
    
    # 4. Prepare Messages for the API
    messages = # /mount/src/gemini-rag-cttm-v6/streamlit_app.py - Inside dhammi_chat function

# 1. Initialize the messages list for the API call
api_messages = []

# 2. Iterate through the history and safely convert to the Gemini SDK Content format
for msg in history:
    # Ensure the content exists and is a string before conversion (Paññā Logic)
    content_text = msg.get("content")
    if content_text and isinstance(content_text, str):
        # Create the Gemini API types.Content object
        api_messages.append(
            types.Content(
                role=msg["role"], 
                parts=[types.Part.from_text(content_text)]
            )
        )

# Add the current user prompt to the list
# We use types.Part.from_text(prompt) directly as we know 'prompt' is the user's string input
api_messages.append(
    types.Content(role="user", parts=[types.Part.from_text(prompt)])
)

# Pass the cleaned, formatted list to the client
# client.models.generate_content(..., contents=api_messages)

    messages.append(types.Content(role="user", parts=[types.Part.from_text(final_user_prompt)]))

    # 5. Gemini API Call
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=1024
            )
        )
        return response.text
        
    except Exception as e:
        return f"🤖 DHAMMI HICCUP (Gemini API Error): {str(e)}. Please check your API key and connection."


# --- DHAMMI CTTM INPUT DASHBOARD (FOR ANONYMOUS UPLOAD) ---

def cttm_input_dashboard():
    st.header("🔗 Ground Truth Submission Link")
    
    st.markdown("""
        **THIS IS THE UPLOAD LINK:** Distribute this link to your trusted network (NGOs, PDF, Junos).
        It is configured for **absolute anonymity** (No sign-in required, no tracing).
        
        <div style="background-color: #ffe0b2; padding: 10px; border-radius: 5px; color: #4e342e;">
        **SAFETY GUARANTEE:** We do not track or store any identifying information.
        </div>
        """, unsafe_allow_html=True)
    
    # NOTE: The actual form link must be obtained by the user after creating the Google Form
    # and setting the sharing permissions.
    st.text_input(
        "Paste Your Google Form Upload Link Here (For Deployment):",
        value="[PASTE YOUR ANONYMOUS GOOGLE FORM LINK HERE]",
        disabled=True
    )
    
    st.markdown("---")
    st.subheader("📝 Junos Insight Data Submission (Preview)")
    
    # The submission form structure for the network to see/use
    with st.form(key="cttm_data_form"):
        st.markdown("**1. The Core Report/Fact (Required)**")
        fact_text = st.text_area(
            "Intelligence:",
            placeholder="E.g., In Ward 3, Bago, NLD verified vote count is 4,500 vs. Military-backed 1,200.",
            height=100
        )
        
        st.markdown("**2. Confidence Level (Paññā Score)**")
        confidence = st.selectbox(
            "Estimated Certainty:",
            ["25% - Possible, Unconfirmed", "50% - Likely, Needs Corroboration", "75% - Highly Likely, Near Verified"]
        )
        
        st.markdown("**3. Junos Tag**")
        junos_tag = st.checkbox(
            "Flag this as urgent/unconfirmed intelligence for Junos Push (CTTM-J)."
        )

        st.markdown("---")
        st.markdown("4. Link to Photo/Evidence (Optional): Please upload files anonymously to Imgur/Drive and paste the link here.")
        evidence_link = st.text_input("Evidence Link:")
        
        # The submission button is cosmetic here, as the final submission happens via the external Google Form link
        submitted = st.form_submit_button("Preview Submit (Use External Link)")

        if submitted:
            st.warning("Please use the external Google Form link above for actual, anonymous submissions.")


# --- STREAMLIT UI LAYOUT ---

def main():
    st.title("🛡️ DHAMMI V6: The SS'ISM Ethical Advisor")
    st.caption(f"Powered by **{MODEL_NAME}** and anchored by **Sīla, Samādhi, Paññā**.")
    
    # Sidebar for Information and the Dashboard Link
    with st.sidebar:
        st.header("Project Details")
        st.write(f"**Developer:** U Ingar Soe")
        st.write("**Model Alignment:** Pro-Democracy, Pro-Federalism (Myanmar)")
        st.markdown("---")
        
        # Display the CTTM Input Dashboard
        cttm_input_dashboard()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User chat input
    if prompt := st.chat_input("Ask Dhammi V6 a question..."):
        # 1. Add user message to history and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Get Dhammi's response
        response = dhammi_chat(prompt, st.session_state.messages)

        # 3. Add assistant response to history and display
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
      

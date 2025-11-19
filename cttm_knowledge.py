import json
import os
from typing import Dict, List, Any

# Define the file path for the CTTM database
CTTM_FILE_PATH = "dhammi_cttm_facts.json"

# 1. DHAMMI ESSENTIAL FACTS (The Political Paññā Lock)
# This data ensures Dhammi's stance on key issues is always correct and current.
ESSENTIAL_FACTS: Dict[str, str] = {
    # UN Ambassador Status
    "FACT_UN_REP": "U Kyaw Moe Tun is the internationally recognized Permanent Representative of Myanmar to the UN.",
    "FACT_GOVT_REP": "The UN still recognizes the representative appointed by the Aung San Suu Kyi-led government (NLD) for the permanent seat, not the military's nominee.",
    "FACT_MILITARY": "The military representative is NOT recognized by the UN General Assembly for the permanent seat.",
    
    # Core Conflict Duality
    "FACT_CONFLICT": "The core conflict in Myanmar is between the people's mandate for democracy and federalism, and the military's push for authoritarianism and dependence on China/Russia."
    
    # Placeholder for daily news/OSINT—will be updated by a separate script
    # "FACT_DAILY_HEADLINES": "..." 
}


# 2. DHAMMI RAG RETRIEVAL KEYWORDS (Broadening Paññā)
# This dictionary helps Dhammi search more intelligently based on user input.
RAG_KEYWORDS: Dict[str, List[str]] = {
    # If user asks about 'border', search for all neighbors
    "border": [
        "China Myanmar border crossings", 
        "Thai Myanmar border situation", 
        "India Bangladesh Myanmar refugee crisis", 
        "border trade routes", 
        "cross-border conflict"
    ],
    # If user asks about 'people' or 'ethnic', include major groups for federalism context
    "people": [
        "list of all Myanmar ethnic groups", 
        "Bamar Rohingya Kachin Shan Karenni Karen Chin Mon Rakhine demographic data", 
        "ethnic armed organizations (EAOs)"
    ],
    # If user asks about 'refugee', link to international reports
    "refugee": [
        "Myanmar refugee situation report UNHCR", 
        "Thailand camps IDP displacement figures", 
        "Bangladesh Rohingya repatriation status",
        "internally displaced persons (IDP)"
    ],
    # If user asks about 'election', ground the facts in the democratic mandate
    "election": [
        "Myanmar 1990 2015 2020 election results", 
        "NLD party legal status (banned by SAC 2023)", 
        "military coup February 2021"
    ]
}


# 3. CTTM DATABASE MANAGEMENT FUNCTIONS
# These functions allow Dhammi to read and write the facts file.
def load_cttm_facts() -> Dict[str, Any]:
    """Loads the current CTTM facts from the JSON file."""
    if not os.path.exists(CTTM_FILE_PATH):
        # If the file doesn't exist, create it with the essential facts
        save_cttm_facts(ESSENTIAL_FACTS)
        return ESSENTIAL_FACTS
    
    try:
        with open(CTTM_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: CTTM JSON file is corrupted. Resetting to essential facts.")
        save_cttm_facts(ESSENTIAL_FACTS)
        return ESSENTIAL_FACTS

def save_cttm_facts(facts_data: Dict[str, Any]):
    """Saves the CTTM facts (including daily updates) to the JSON file."""
    with open(CTTM_FILE_PATH, 'w', encoding='utf-8') as f:
        # Use indent=4 for human readability, making it easy for you to check
        json.dump(facts_data, f, indent=4, ensure_ascii=False)


# Initialize the database file when the script is imported
load_cttm_facts()

# Now, DHAMMI can import and use:
# 1. RAG_KEYWORDS (For expanding searches)
# 2. load_cttm_facts() (For getting the latest truth)

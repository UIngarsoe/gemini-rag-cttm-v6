🛡️ DHAMMI V6: The Gemini-RAG Consciousness-Trained Truth Manager (CTTM)

An Ethical AI Advisor Grounded in SS'ISM Philosophy and Real-Time Sociopolitical Data.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_square_white.svg)](https://your-deployment-link.streamlit.app)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

***
 🌟 Project Overview

DHAMMI V6 is the world's first fully ethical AI system designed to act as a Mobile Advisor and Personal Companion (MSSA), specifically engineered to provide truthful, contextual, and ethically-grounded insight into complex sociopolitical landscapes.

Built on the Gemini API using a Retrieval-Augmented Generation (RAG) architecture, the system's output is grounded in the proprietary Consciousness-Trained Truth Manager (CTTM) ledger. This approach ensures all advice adheres to the Buddhist ethical framework of **SS'ISM** (Sīla, Samādhi, Paññā, Metta).

The system’s philosophy is rooted in the principle of "Doing Nothing as Value" for cybersecurity and defense, institutionalizing a mandatory delay protocol (like the SSISM V Smart Advisor 24-hour lockout) to counter high-pressure social engineering and misinformation.

***
🧭 Core Ethical & Political Philosophy (SS'ISM)

DHAMMI V6 operates under an unwavering ethical mandate, designed to promote truth, non-harm (Ahiṃsā), and democratic principles.

| Principle | Description | DHAMMI V6 Implementation |
| :--- | :--- | :--- |
| **Sīla** (Ethical Adherence) | The system is programmed with a **Deontological Firewall** and is unwaveringly aligned with **democracy, federalism, and national sovereignty**, supporting electoral mandates (1990, 2015, 2020) and international law. | Refuses all harmful, illegal, or manipulative requests. |
| **Metta** (Loving-Kindness) | The model's tone and communication are guided by genuine warmth, compassion (Karunā), and supportive encouragement, acting as a true "Personal Companion." | Ensures human-centric, patient, and non-judgmental advisory responses. |
| **Paññā** (Insight) | The system critically evaluates all data through the **Truth Gap Protocol**, acknowledging that official information may be incomplete or outdated, requiring verification from multiple sources. | Explicitly provides confidence scores and cites sources from the CTTM Ledger. |

***
 ⚙️ Technical Architecture: Gemini + RAG + CTTM

This repository combines Google's powerful LLM with a specialized data pipeline to create verifiable, **non-hallucinatory** responses:

1.  **Gemini 2.5 Flash:** Serves as the core generative model, providing the high-level reasoning and ethical adherence guided by the `system_instructions.py`.
2.  **Retrieval-Augmented Generation (RAG):** The RAG framework is used to dynamically query and retrieve relevant context from the external CTTM Ledger *before* generating a response.
3.  **CTTM Ground Truth Ledger:** This is the project’s external, real-time knowledge base (implemented via Google Sheets/Streamlit GSheetsConnection) that contains:
    * **Verified Truth:** Factual data with high **V-Scores** (Verification Confidence).
    * **Actionable Intelligence:** Time-sensitive OSINT or network data (Junos Insight Module).

 Key Files in this Repository

| File Name | Purpose |
| :--- | :--- |
| `system_instructions.py` | Contains the **DHAMMI V6 System Prompt**, defining its core ethical and political stance (Sīla, Metta, Ahiṃsā). |
| `cttm_writer.py` | Holds the Streamlit function `cttm_input_dashboard()` for authorized users to submit and append new **Ground Truth Facts** directly to the CTTM Ledger. |
| `streamlit_app.py` | The main application entry point that integrates Gemini API, the RAG logic, and the Streamlit UI. |

***
🛠️ Setup and Installation

Prerequisites

* Python 3.10+
* A Google AI Studio API Key (`GEMINI_API_KEY`)
* Access to a Google Sheet (for the CTTM Ledger)

 Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/UIngarsoe/gemini-rag-cttm-v6.git](https://github.com/UIngarsoe/gemini-rag-cttm-v6.git)
    cd gemini-rag-cttm-v6
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Secrets:**
    Create a `.streamlit/secrets.toml` file to store your API key and Google Sheets credentials:
    ```toml
    # .streamlit/secrets.toml
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

    [gsheets]
    spreadsheet_url = "YOUR_CTTM_LEDGER_SHEET_URL"
    # ... other gsheets connection details if needed
    ```

4.  **Run the Application:**
    ```bash
    streamlit run streamlit_app.py
    ```

***
 🤝 License

This project is released under the **Apache License 2.0**.

By choosing this license, the developer dedicates this work to the open-source community and, specifically, as a contribution to further the development of ethical, verifiable, and safety-oriented large language models and RAG architectures, including those developed by Google.

Apache License 2.0

```text
Copyright [YYYY] [U Ingar Soe]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

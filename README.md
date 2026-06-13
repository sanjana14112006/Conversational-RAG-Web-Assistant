# Conversational RAG Website Virtual Assistant 🤖

An advanced, private conversational customer support assistant built from scratch using **LangChain LCEL**, **Flask**, **ChromaDB**, and the **Gemini-2.5-Flash** model.

## 🚀 Key Architectural Features
- **Conversational Memory:** Backed by a persistent **SQLite database** to retain context across system restarts.
- **Smart Intent Routing:** Dynamically categorizes incoming queries (`GREETING`, `COMPANY_QUERY`, `OUT_OF_BOUNDS`) to safeguard AI guardrails.
- **Automated Scraping Engine:** Uses a custom recursive crawler to strip away web markup clutter and parse clean facts.
- **Verified Link Citations:** Maps retrieved document metadata back into live, clickable frontend hyperlinks.

## 🛠️ Local Sandbox Installation
1. Clone this repository onto your machine.
2. Create a `.env` file containing your `GOOGLE_API_KEY`.
3. Install dependencies: `pip install -r requirements.txt`
4. Run `python ingest.py` to compile the local knowledge base.
5. Boot up the live web environment: `python app.py`

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


# 🚀 Installation & Setup

## Prerequisites
* Python 3.11
* A valid `GOOGLE_API_KEY` (Gemini API access authentication token)

## Step-by-Step Installation

### 1. Clone the Repository:
```bash
git clone [https://github.com/sanjana14112006/Conversational-RAG-Web-Assistant.git](https://github.com/sanjana14112006/Conversational-RAG-Web-Assistant.git)
cd Conversational-RAG-Web-Assistant

### 2. Create and Activate a Virtual Environment:
```bash
py -3.11 -m venv .venv
.\.venv\Scripts\activate.bat

### 3. Configure Local Credentials:
Create a new file named `.env` in the root directory of the project and paste your secret Gemini API access token inside it:
```text
GOOGLE_API_KEY=your_actual_gemini_api_key_here

### 4. Install Dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt

### 5. Compile the Local Vector Database:
Run the ingestion pipeline to parse the target website, scrub the HTML noise, extract text chunks, and generate the mathematical indices locally:
```bash
python ingest.py

### 6. Execute the Application:
Launch the local Flask application server architecture:
```bash
python app.py



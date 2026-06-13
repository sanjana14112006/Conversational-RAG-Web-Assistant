import os
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from bs4 import BeautifulSoup

def clean_and_extract_text(html_content):
    """
    LOGIC: Raw web code contains massive amounts of repetitive, non-informative data 
    like cookie popups, styling scripts, and navigation links. 
    This function intercepts the HTML page, uses BeautifulSoup to parse it, and completely 
    deletes non-text containers before saving. This guarantees our AI database contains 
    only high-quality, readable company facts.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Identify and permanently strip away noisy web components
    for junk_element in soup(["script", "style", "header", "footer", "nav", "form", "aside"]):
        junk_element.decompose()
        
    # Extract the remaining raw text strings separated by a clean space
    raw_text = soup.get_text(separator=" ")
    
    # Strip away massive clumps of empty line-breaks and tab spacing
    clean_text = " ".join(raw_text.split())
    return clean_text

def build_centralized_knowledge_base(target_website):
    """
    LOGIC: This controls the multi-page loading pipeline. It crawls the target 
    website up to a structured depth boundary, formats the text, chunks it, 
    and saves the mathematical vectors into a centralized database folder.
    """
    print(f"🕵️‍♂️ Step 1: Starting recursive web crawl on: {target_website}")
    
    # max_depth=2 loads the homepage (depth 1), grabs all its internal menu/footer links,
    # and automatically navigates and scrapes those sub-pages too (depth 2).
    loader = RecursiveUrlLoader(
        url=target_website,
        max_depth=2,
        extractor=clean_and_extract_text
    )
    
    # Pull the cleaned textual layouts from all discovered web links into a list
    raw_documents = loader.load()
    
    if not raw_documents:
        print("❌ Error: No text could be pulled from the target URL. Check your internet connection or the website's accessibility.")
        return
        
    print(f"📄 Successfully loaded and scrubbed text from {len(raw_documents)} distinct pages.")

    print("✂️ Step 2: Splitting giant web pages into optimized paragraphs...")
    # Slicing documents into 600-character pieces keeps chunks dense and relevant.
    # An overlap of 100 characters makes sure sentences that get split maintain context.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    final_chunks = text_splitter.split_documents(raw_documents)
    print(f"🧩 Created {len(final_chunks)} semantic chunks for the unified database.")

    print("📦 Step 3: Activating local HuggingFace embedding engine (all-MiniLM-L6-v2)...")
    # This model turns text paragraphs into mathematical vector arrays on your laptop's memory
    embedding_engine = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("💾 Step 4: Storing text vectors locally inside the './chroma_db' folder...")
    # This initializes ChromaDB and dumps all data from every page into one centralized spot
    vector_store = Chroma.from_documents(
        documents=final_chunks,
        embedding=embedding_engine,
        persist_directory="./chroma_db"
    )
    print("✅ Centralized Database Setup Complete! All pages are memorized inside './chroma_db'.")

if __name__ == "__main__":
    # --- TARGET CONFIGURATION ---
    # Replace this target link with the homepage of the company website you are building for!
    # Tip: Test it with a lightweight public informational site or playground address first.
    company_site_url = "http://books.toscrape.com/" 
    
    build_centralized_knowledge_base(company_site_url)
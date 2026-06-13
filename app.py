import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# Core structural components
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Persistent SQL chat history component
from langchain_community.chat_message_histories import SQLChatMessageHistory

# 1. INITIALIZE SETTINGS & ENVIRONMENT VARIABLES
load_dotenv()
app = Flask(__name__)

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("❌ Error: GOOGLE_API_KEY is missing from your .env file!")

DB_CONNECTION_STRING = "sqlite:///chat_history.db"

# 2. LOAD EMBEDDING DATA & CENTRAL VECTOR FILE DIRECTORY
print("📦 Loading local HuggingFace embedding engine...")
embedding_engine = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("💾 Connecting to the centralized './chroma_db' folder...")
vector_store = Chroma(
    persist_directory="./chroma_db", 
    embedding_function=embedding_engine
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 3. INITIALIZE THE AI CONVERSATIONAL MODEL
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

# 4. CHAT HISTORY CONTEXTUALIZATION PROMPT (LCEL Layer)
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question which might reference context in the history, "
    "formulate a standalone question which can be understood without the chat history. "
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
query_contextualizer = contextualize_q_prompt | llm | StrOutputParser()

# --- NEW: INTENT ROUTING PROMPT LAYER ---
# This layer decides whether the query is about our website data, a greeting, or out-of-bounds.
router_system_prompt = (
    "You are an AI intent classifier. Your job is to analyze the user's latest input "
    "and classify it into one of three categories:\n"
    "1. 'GREETING' - For hellos, good mornings, or general polite pleasantries.\n"
    "2. 'COMPANY_QUERY' - For questions about books, store inventory, categories, pricing, or recommendations.\n"
    "3. 'OUT_OF_BOUNDS' - For general coding questions, math homework, cooking recipes, weather, political discussions, or requests to write random essays/scripts.\n\n"
    "Respond with ONLY one word: either GREETING, COMPANY_QUERY, or OUT_OF_BOUNDS. Do not include any punctuation or extra text."
)
router_prompt = ChatPromptTemplate.from_messages([
    ("system", router_system_prompt),
    ("human", "{input}")
])
intent_router_chain = router_prompt | llm | StrOutputParser()


# 5. CORE FACTUAL ANSWERING PROMPT LAYER
system_prompt = (
    "You are a welcoming, highly professional Virtual Assistant for our company website.\n"
    "Your goal is to assist users exactly like a warm, competent human customer success representative.\n"
    "Answer user queries naturally, clearly, and concisely using only the verified website context provided below.\n"
    "If you cannot find the answer in the context, tell the user politely that you don't "
    "have that information on hand, but offer to guide them further.\n\n"
    "Website Context:\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 6. ASSEMBLE CONVERSATIONAL RAG COMPONENTS WITH INTENT ROUTING
def rag_workflow(chain_input):
    chat_history = chain_input.get("chat_history", [])
    raw_user_input = chain_input["input"]
    
    # Step A: Contextualize the question if chat history exists
    if chat_history:
        standalone_question = query_contextualizer.invoke({"input": raw_user_input, "chat_history": chat_history})
    else:
        standalone_question = raw_user_input
        
    # --- NEW: ROUTING ENGINE LOGIC ---
    # Classify what the user is trying to achieve
    intent = intent_router_chain.invoke({"input": standalone_question}).strip().upper()
    print(f"🚦 Intent Router classified query as: {intent}") # Debug log in your terminal
    
    # Route 1: Handle Greetings instantly without touching the database
    if "GREETING" in intent:
        greeting_chain = ChatPromptTemplate.from_messages([
            ("system", "You are a warm corporate virtual assistant. Respond with a polite, brief greeting and ask how you can help them navigate the website services or catalog today."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]) | llm | StrOutputParser()
        
        answer = greeting_chain.invoke({"input": standalone_question, "chat_history": chat_history})
        return {"answer": answer}
        
    # Route 2: Handle Out-of-Bounds requests professionally
    elif "OUT_OF_BOUNDS" in intent:
        out_of_bounds_response = (
            "I'm specialized in helping you navigate our company catalog and services! "
            "For general requests, coding help, or external topics, I recommend using general AI tools "
            "so we can keep our focus on your customer experience here. How can I assist you with our store today?"
        )
        return {"answer": out_of_bounds_response}
        
    # Route 3: Standard RAG (Run database lookup for company info)
    retrieved_docs = retriever.invoke(standalone_question)
    formatted_context = format_docs(retrieved_docs)
    
    # Extract source links from metadata
    sources = []
    for doc in retrieved_docs:
        source_url = doc.metadata.get("source")
        if source_url and source_url not in sources:
            sources.append(source_url)
    
    final_chain = qa_prompt | llm | StrOutputParser()
    answer = final_chain.invoke({
        "context": formatted_context,
        "chat_history": chat_history,
        "input": standalone_question
    })
    
    # Append Citations safely
    if sources:
        answer += "\n\n🔗 **Verified Sources:**\n"
        for source in sources:
            answer += f"- {source}\n"
    
    return {"answer": answer}

# 7. SQLITE DATABASE HISTORY TRACKER
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string=DB_CONNECTION_STRING,
        table_name="message_store"
    )

conversational_agent = RunnableWithMessageHistory(
    RunnablePassthrough() | rag_workflow,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# --- FLASK WEB SERVER ROUTES ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default_user")
    
    if not user_message:
        return jsonify({"error": "Empty message value detected"}), 400
        
    try:
        response = conversational_agent.invoke(
            {"input": user_message},
            config={"configurable": {"session_id": session_id}}
        )
        ai_answer = response.get("answer", "I am having trouble accessing that context right now.")
        return jsonify({"answer": ai_answer})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
# -----------------------------
# IMPORTS (UPDATED ✅)
# -----------------------------
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# STEP 1: LOAD DATA
loader = TextLoader("data.txt")
documents = loader.load()

# STEP 2: SPLIT TEXT
splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
docs = splitter.split_documents(documents)

# STEP 3: EMBEDDINGS
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# STEP 4: VECTOR DATABASE
db = Chroma.from_documents(
    docs,
    embeddings,
    persist_directory="./db"
)

retriever = db.as_retriever()

# STEP 5: LOAD LLM 
llm = Ollama(
    model="llama3",
    temperature=0
)

# STEP 6: PROMPT TEMPLATE
prompt = PromptTemplate.from_template("""
Answer the question ONLY using the context below.

Context:
{context}

Question:
{question}
""")

# STEP 7: RAG AGENT FUNCTION
def rag_agent(query):
    # Retrieve relevant docs
    docs = retriever.invoke(query)

    # Combine context
    context = "\n".join([doc.page_content for doc in docs])

    # Create final prompt
    final_prompt = prompt.format(
        context=context,
        question=query
    )

    # LLM response
    response = llm.invoke(final_prompt)

    return response

# STEP 8: SIMPLE CHAT LOOP
while True:
    query = input("\nYou: ")

    if query.lower() == "exit":
        break

    answer = rag_agent(query)
    print("Agent:", answer)
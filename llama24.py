from flask import Flask, request, jsonify
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all domains during development


import os




# Set tokenizers parallelism to false to avoid warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

app = Flask(__name__)
CORS(app)  # Allow CORS for all domains during development


# Paths and constants
DB_FAISS_PATH = "vectorstore/db_faiss"
MODEL_PATH = "models/llama-2-7b-chat.ggmlv3.q4_0.bin"
CSV_PATH = "data/in.csv"

# Load CSV data
loader = CSVLoader(file_path=CSV_PATH, encoding="utf-8", csv_args={'delimiter': ','})
data = loader.load()

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
text_chunks = text_splitter.split_documents(data)

# Load embeddings
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

# Create FAISS vector store
docsearch = FAISS.from_documents(text_chunks, embeddings)
docsearch.save_local(DB_FAISS_PATH)

# Initialize LLM
llm = CTransformers(model=MODEL_PATH, model_type="llama", max_new_tokens=512, temperature=0.1)
qa = ConversationalRetrievalChain.from_llm(llm, retriever=docsearch.as_retriever())

# Define endpoint for query
@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data.get('query')
    chat_history = data.get('chat_history', [])

    if not query:
        return jsonify({"error": "Query is required"}), 400

    result = qa({"question": query, "chat_history": chat_history})
    return jsonify({"answer": result['answer']})

if __name__ == '__main__':
    app.run(debug=True)

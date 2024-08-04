from flask import Flask, request, jsonify
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain
import guardrails as gd

# Initialize Flask app
app = Flask(__name__)

DB_FAISS_PATH = "vectorstore/db_faiss"

# Load data
loader = CSVLoader(file_path="data/in.csv", encoding="utf-8", csv_args={'delimiter': ','})
data = loader.load()

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
text_chunks = text_splitter.split_documents(data)

# Download Sentence Transformers Embedding From Hugging Face
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

# Create FAISS vector store
docsearch = FAISS.from_documents(text_chunks, embeddings)
docsearch.save_local(DB_FAISS_PATH)

# Initialize the LLM
llm = CTransformers(model="models/llama-2-7b-chat.ggmlv3.q4_0.bin",
                    model_type="llama",
                    max_new_tokens=512,
                    temperature=0.1)

qa = ConversationalRetrievalChain.from_llm(llm, retriever=docsearch.as_retriever())

# Define the guardrails configuration with specific input guards
guard = gd.Rail(
    input_schema={
        "query": gd.Field(type=str, required=True),
        "chat_history": gd.Field(type=list, required=False, default=[])
    },
    output_schema={
        "answer": gd.Field(type=str)
    },
    input_guardrails=[
        gd.Checks.no_personal_information(),  # Check for PII
        gd.Checks.no_off_topic(),              # Check for off-topic queries
        gd.Checks.no_jailbreak_attempts()      # Check for jailbreak attempts
    ],
    output_guardrails=[
        gd.Checks.no_hate_speech(),
        gd.Checks.length(max_length=1500),  # Limit response length
        gd.Checks.no_hallucination(),
    ]
)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data.get('query')
    chat_history = data.get('chat_history', [])
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    # Validate inputs with Guardrails
    try:
        validated_input = guard.validate_input(data)
    except gd.ValidationError as e:
        return jsonify({"error": str(e)}), 400

    # Process the query
    result = qa({"question": validated_input['query'], "chat_history": validated_input['chat_history']})
    
    # Validate outputs with Guardrails
    validated_output = guard.validate_output({"answer": result['answer']})

    return jsonify(validated_output)

if __name__ == '_main_':
    app.run(debug=True)
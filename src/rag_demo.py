import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

load_dotenv()

# 1. Init vector DB (Chroma in-memory)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="docs")

docs = [
    "Python is a popular programming language created by Guido van Rossum.",
    "RAG stands for Retrieval-Augmented Generation.",
    "OpenAI develops GPT models for natural language processing."
]

# 2. Add documents to vector store
for i, doc in enumerate(docs):
    collection.add(
        documents=[doc],
        ids=[str(i)]
    )

# 3. User query
query = "Who created Python?"
system_prompt = "Answer based only on the context."

# 4. Retrieve relevant chunks
results = collection.query(
    query_texts=[query],
    n_results=2
)
retrieved_docs = results["documents"][0]

# 5. Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_KEY"),base_url=os.getenv("OPENAI_URL"))

# 6. Use typed message objects for ChatCompletion
messages: list = [
    # ChatCompletionSystemMessageParam(content=system_prompt,role="system"),
    ChatCompletionUserMessageParam(content=f"Context: {retrieved_docs}\n\nQuestion: {query}",role="user"),
]

response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=messages,
            )

# 7. Print the answer
print("Answer:", response.choices[0].message.content)

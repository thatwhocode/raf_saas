from qdrant_client import QdrantClient
from ollama import Client

qdrant_client = QdrantClient(url="http://localhost:6333")
ollama_client = Client(host="http://localhost:11434")

def ask_about_cv(question: str):
    print(f"🤔 Думаю над питанням: '{question}'...\n")


    query_vector = ollama_client.embeddings(model="nomic-embed-text", prompt=question)["embedding"]
    response = qdrant_client.query_points(
        collection_name="cv_nodes",
        query=query_vector,
        limit=3  
    )
    search_results = response.points 

    context = ""
    for hit in search_results:
        context += hit.payload["text"] + "\n---\n"


    system_prompt = f"""You are an HR assistant analyzing a candidate's CV. 
    Answer the user's question based ONLY on the context provided below. 
    If the answer is not in the context, say "I don't have this information".
    
    Context from CV:
    {context}
    """


    response = ollama_client.chat(model='llama3', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': question}
    ])

    print("✅ ВІДПОВІДЬ:")
    print(response['message']['content'])
    print("\n" + "="*50 + "\n")
    print("🔍 Використані шматки резюме (для дебагу):")
    for i, hit in enumerate(search_results):
        print(f"[{i+1}] (Схожість: {hit.score:.2f}) -> {hit.payload['text'][:100]}...")

if __name__ == "__main__":

    ask_about_cv("What is Stanislav's main tech stack and what did he use Python for?")
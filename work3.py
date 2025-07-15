from openai import OpenAI
import faiss
import numpy as np

client = OpenAI(api_key="")

notes = []
note_embeddings = []

dim = 1536
index = faiss.IndexFlatL2(dim)

def add_note(text):
    resp = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = np.array(resp.data[0].embedding, dtype=np.float32)
    
    notes.append(text)
    note_embeddings.append(embedding)
    index.add(np.array([embedding]))
    print(f"Added note: {text}")

def search_notes(query, top_k=2):
    resp = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    q_emb = np.array(resp.data[0].embedding, dtype=np.float32)
    _, I = index.search(np.array([q_emb]), top_k)
    
    results = [notes[i] for i in I[0] if i != -1]
    return results

def ask_assistant(question):
    relevant = search_notes(question)
    context = "\n".join(relevant)
    
    messages = [
        {"role": "system", "content": "You are a helpful research assistant."},
        {"role": "user", "content": question},
        {"role": "assistant", "content": f"Here are some related notes:\n{context}"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

if __name__ == "__main__":
   
    q = "who is ms dhoni"
    answer = ask_assistant(q)
    print(f"Q: {q}\nA: {answer}")

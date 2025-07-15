from openai import OpenAI
import faiss
import numpy as np
import json
import httpx
client = OpenAI(api_key="")
notes = []
note_embeddings = []
dim = 1536
index = faiss.IndexFlatL2(dim)
def add_note(text):
    resp = client.embeddings.create(input=text, model="text-embedding-3-small")
    embedding = np.array(resp.data[0].embedding, dtype=np.float32)
    notes.append(text)
    note_embeddings.append(embedding)
    index.add(np.array([embedding]))
    print(f" Note added: {text}")
def search_notes(query, top_k=2):
    resp = client.embeddings.create(input=query, model="text-embedding-3-small")
    q_emb = np.array(resp.data[0].embedding, dtype=np.float32)
    _, I = index.search(np.array([q_emb]), top_k)
    return [notes[i] for i in I[0] if i != -1]
def web_search(brave):
    print(f" Performing web search for: {brave}")
    return [
        f"Web result 1 about '{brave}'",
        f"Web result 2 about '{brave}'"
    ]
def ask_assistant(question):
    functions = [
        {
            "name": "search_notes",
            "description": "Search research notes by query",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            },
        },
        {
            "name": "web_search",
            "description": "Perform a real-time web search for current information",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            },
        }
    ]

    messages = [
        {"role": "system", "content": "You are a helpful AI research assistant."},
        {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    message = response.choices[0].message
    if getattr(message, "function_call", None):
        func_name = message.function_call.name
        args = json.loads(message.function_call.arguments)

        if func_name == "search_notes":
            results = search_notes(args["query"])
            return " Notes:\n" + "\n".join(results)
        elif func_name == "web_search":
            results = web_search(args["query"])
            return " Web Results:\n" + "\n".join(results)
        else:
            return f" Unknown function called: {func_name}"

    return message.content

if __name__ == "__main__":
    question = "tell about baahubali movie "
    answer = ask_assistant(question)
    print(f"\nQ: {question}\nA: {answer}")

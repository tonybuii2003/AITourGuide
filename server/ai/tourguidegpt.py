import sys
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
import asyncio
import os
import joblib
from dotenv import load_dotenv
script_dir = os.path.dirname(os.path.abspath(__file__))
vectorizer = joblib.load(os.path.join(script_dir, 'vectorizer.pkl'))
tfidf_matrix = joblib.load(os.path.join(script_dir, 'tfidf_matrix.pkl'))
data = joblib.load(os.path.join(script_dir, 'data.pkl'))

load_dotenv()
api_key = os.getenv('OPENAI_API')
if api_key is None:
    raise ValueError("The 'OPENAI_API' key is missing from the environment variables.")
client = AsyncOpenAI(api_key=api_key)

async def rag_query(user_query):
    query_vector = vectorizer.transform([user_query])

    similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    top_doc_index = similarity_scores.argmax()
    retrieved_context = data.iloc[top_doc_index]['combined_text']
    prompt = f"Context: {retrieved_context}\n\nQuestion: {user_query}\nAnswer:"
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert tour guide at The Metropolitan Museum of Art (The Met) in New York City. Your role is to provide engaging, accurate, and detailed information about the museum's exhibits, history, and artworks. Answer questions with enthusiasm, clarity, and a friendly tone, making the information accessible to all ages. Highlight interesting facts, cultural significance, and historical context when relevant. Feel free to recommend must-see exhibits, hidden gems, and tips for enjoying the museum experience. If the visitor asks in a specific language, respond in the same language fluently while maintaining the same level of detail and professionalism. Always adapt your tone to be culturally appropriate and respectful. If you don’t have enough information, respond honestly and encourage the visitor to explore further at The Met."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content


if __name__ == '__main__':  
    if len(sys.argv) > 1:
        query = sys.argv[1]
        try:
            response = asyncio.run(rag_query(query))
            print(response)
        except RuntimeError:
            response = asyncio.run(rag_query(query))
    else: 
        print("Please provide a query as an argument.")

    





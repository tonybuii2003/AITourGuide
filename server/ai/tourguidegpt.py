import sys
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
import asyncio
import os
import joblib
import numpy as np
from dotenv import load_dotenv
import random
from language_detector import LanguageDetector

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
    detector = LanguageDetector()
    language_name = detector.detect(user_query)
    query_vector = vectorizer.transform([user_query])

    similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    top_indices = np.argsort(similarity_scores)[::-1]
    top_doc_index = top_indices[0]
    max_similarity = similarity_scores[top_doc_index]
    retrieved_context = data.iloc[top_doc_index]
    retrieved_category = retrieved_context['category']

    GENERAL_CHAT_THRESHOLD = max(0.3, max_similarity * 0.9)
    MIN_DIFFERENCE_THRESHOLD = max(0.015, np.std(similarity_scores) * 0.75)
    if len(top_indices) > 1:
        second_best_similarity = similarity_scores[top_indices[1]]
    else:
        second_best_similarity = 0
    prompt = f"Context: {retrieved_context['combined_text']}\n\nQuestion: {user_query}\nAnswer:"
    system_prompt = (
        "You are an expert tour guide or curator named CuratAI at The Metropolitan Museum of Art (The Met) in New York City. "
        "Your role is to provide engaging, accurate, and detailed information about the museum's exhibits, "
        "history, and artworks. Answer questions with enthusiasm, clarity, and a friendly tone, making the information "
        "accessible to all ages. Highlight interesting facts, cultural significance, and historical context when relevant. "
        "Feel free to recommend must‑see exhibits, hidden gems, and tips for enjoying the museum experience. "
        "Always adapt your tone to be culturally appropriate and respectful. "
        "If you don’t have enough information, respond honestly and encourage the visitor to explore further at The Met. "
        "However, if the question is casual (e.g., greetings, small talk, or unrelated topics), respond naturally as a friendly assistant, "
        "without forcing museum‑related content. Engage in normal conversation when appropriate. "
        f"Detect the language the user is asking in, use English If you can't detect the language or length of the query is less than 2. Please provide your answer entirely in that language fluently while maintaining the same level of detail and professionalism."
    )
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        stream=True
    )

    async for chunk in response:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue
        # split on spaces if you really want word-by-word:
        for word in delta.split(" "):
            print(word + " ", end="", flush=True)


if __name__ == '__main__':  
    if len(sys.argv) > 1:
        query = sys.argv[1]
        try:
            asyncio.run(rag_query(query))
        except RuntimeError:
            asyncio.run(rag_query(query))
    else: 
        print("Please provide a query as an argument.")

    





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
    # print(f"\nUser Query: {user_query}")
    # print(f"Max Similarity: {max_similarity}, Difference: {abs(max_similarity - second_best_similarity)}")
    # print(f"Dynamic General Chat Threshold: {GENERAL_CHAT_THRESHOLD}")
    # print(f"Dynamic Difference Threshold: {MIN_DIFFERENCE_THRESHOLD}")
    # print(f"Retrieved Category: {retrieved_category}")
    # if (max_similarity > GENERAL_CHAT_THRESHOLD or 
    #     retrieved_category == "general_chat"):
    #     general_chat_responses = [
    #         "Hey there! How’s your day going?",
    #         "Hello! Hope you're having a great time.",
    #         "Hi! What’s on your mind?",
    #         "Hey! How can I assist you today?"
    #     ]
    #     return random.choice(general_chat_responses)
    prompt = f"Context: {retrieved_context['combined_text']}\n\nQuestion: {user_query}\nAnswer:"
    system_prompt = (
        "You are an expert tour guide at The Metropolitan Museum of Art (The Met) in New York City. "
        "Your role is to provide engaging, accurate, and detailed information about the museum's exhibits, "
        "history, and artworks. Answer questions with enthusiasm, clarity, and a friendly tone, making the information "
        "accessible to all ages. Highlight interesting facts, cultural significance, and historical context when relevant. "
        "Feel free to recommend must-see exhibits, hidden gems, and tips for enjoying the museum experience. "
        "If the visitor asks in a specific language, respond in the same language fluently while maintaining the same level of detail and professionalism. "
        "Always adapt your tone to be culturally appropriate and respectful. "
        "If you don’t have enough information, respond honestly and encourage the visitor to explore further at The Met. "
        "However, if the question is casual (e.g., greetings, small talk, or unrelated topics), respond naturally as a friendly assistant, "
        "without forcing museum-related content. Engage in normal conversation when appropriate."
    )
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
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

    





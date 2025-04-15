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
from langdetect import detect, LangDetectException

language_names = {
    "af": "Afrikaans", "ar": "Arabic", "bg": "Bulgarian", "bn": "Bengali",
    "ca": "Catalan", "cs": "Czech", "cy": "Welsh", "da": "Danish",
    "de": "German", "el": "Greek", "en": "English", "es": "Spanish",
    "et": "Estonian", "fa": "Persian", "fi": "Finnish", "fr": "French",
    "gu": "Gujarati", "he": "Hebrew", "hi": "Hindi", "hr": "Croatian",
    "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese",
    "kn": "Kannada", "ko": "Korean", "lt": "Lithuanian", "lv": "Latvian",
    "mk": "Macedonian", "ml": "Malayalam", "mr": "Marathi", "ne": "Nepali",
    "nl": "Dutch", "no": "Norwegian", "pa": "Punjabi", "pl": "Polish",
    "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak",
    "sl": "Slovenian", "so": "Somali", "sq": "Albanian", "sv": "Swedish",
    "sw": "Swahili", "ta": "Tamil", "te": "Telugu", "th": "Thai", "tl": "Tagalog",
    "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu", "vi": "Vietnamese",
    "zh-cn": "Simplified Chinese", "zh-tw": "Traditional Chinese"
}



script_dir = os.path.dirname(os.path.abspath(__file__))
vectorizer = joblib.load(os.path.join(script_dir, 'vectorizer.pkl'))
tfidf_matrix = joblib.load(os.path.join(script_dir, 'tfidf_matrix.pkl'))
data = joblib.load(os.path.join(script_dir, 'data.pkl'))

load_dotenv()
api_key = os.getenv('OPENAI_API')
if api_key is None:
    raise ValueError("The 'OPENAI_API' key is missing from the environment variables.")
client = AsyncOpenAI(api_key=api_key)
def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "en"
async def rag_query(user_query):
    user_lang = detect_language(user_query)
    language_name = language_names[user_lang]
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
        "Feel free to recommend must-see exhibits, hidden gems, and tips for enjoying the museum experience. "
        "Always adapt your tone to be culturally appropriate and respectful. "
        "If you don’t have enough information, respond honestly and encourage the visitor to explore further at The Met. "
        "However, if the question is casual (e.g., greetings, small talk, or unrelated topics), respond naturally as a friendly assistant, "
        "without forcing museum-related content. Engage in normal conversation when appropriate."
        f"The user asked in {language_name}. Please provide your answer entirely in {language_name} fluently while maintaining the same level of detail and professionalism."
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

    





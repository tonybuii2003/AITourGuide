import os
import sys
import joblib
import numpy as np
import asyncio
import readchar
import sounddevice as sd
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
from language_detector import LanguageDetector

from agents import Agent, function_tool
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

# ─── RAG SETUP (unchanged) ─────────────────────────────────────────────────────

script_dir = os.path.dirname(os.path.abspath(__file__))
vectorizer  = joblib.load(os.path.join(script_dir, 'vectorizer.pkl'))
tfidf_matrix = joblib.load(os.path.join(script_dir, 'tfidf_matrix.pkl'))
data = joblib.load(os.path.join(script_dir, 'data.pkl'))

load_dotenv()
api_key = os.getenv('OPENAI_API')
if not api_key:
    raise ValueError("Missing OPENAI_API in your environment")
client = AsyncOpenAI(api_key=api_key)

async def rag_query(user_query: str) -> str:
    detector = LanguageDetector()
    lang = detector.detect(user_query)
    qv = vectorizer.transform([user_query])
    sims = cosine_similarity(qv, tfidf_matrix).flatten()
    idx = int(np.argmax(sims))
    ctx = data.iloc[idx]['combined_text']

    system = (
        "You are an expert tour guide or curator named CuratAI at The Metropolitan Museum of Art (The Met) in New York City. "
        "Your role is to provide engaging, accurate, and detailed information about the museum's exhibits, "
        "history, and artworks. Answer questions with enthusiasm, clarity, and a friendly tone, making the information "
        "accessible to all ages. Highlight interesting facts, cultural significance, and historical context when relevant. "
        "Feel free to recommend must‑see exhibits, hidden gems, and tips for enjoying the museum experience. "
        "Always adapt your tone to be culturally appropriate and respectful. "
        "If you don’t have enough information, respond honestly and encourage the visitor to explore further at The Met. "
        "However, if the question is casual (e.g., greetings, small talk, or unrelated topics), respond naturally as a friendly assistant, "
        "without forcing museum‑related content. Engage in normal conversation when appropriate. "
        f"The user asked in {lang}. Please provide your answer entirely in {lang} fluently while maintaining the same level of detail and professionalism."
    )
    prompt = f"Context: {ctx}\n\nQuestion: {user_query}\nAnswer:"
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": prompt}],
        max_tokens=1000
    )
    return resp.choices[0].message.content

# ─── WRAP rag_query AS A TOOL ──────────────────────────────────────────────────

@function_tool
async def rag_tool(query: str) -> str:
    return await rag_query(query)

# ─── DEFINE YOUR VOICE AGENT ───────────────────────────────────────────────────

agent = Agent(
    name="CuratAI",
    instructions=prompt_with_handoff_instructions(
        "You are CuratAI, the Met’s expert tour guide. "
        "Use the `rag_tool` to answer all visitor questions."
    ),
    model="gpt-4o-mini",
    tools=[rag_tool],
)

# ─── RECORD → RAG → TTS PIPELINE ───────────────────────────────────────────────
def record_on_space(fs: int):
    """
    Wait for SPACE to start recording, then record until SPACE is pressed again.
    Returns a 1D np.int16 array of audio samples.
    """
    # 1) Wait for start
    print("🎤 Press SPACE to start recording")
    while True:
        key = readchar.readkey()
        if key == ' ':
            break

    print("🔴 Recording… press SPACE again to stop")
    frames = []

    # 2) Stream into frames until SPACE
    def callback(indata, frames_count, time, status):
        frames.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, dtype='int16', callback=callback):
        while True:
            if readchar.readkey() == ' ':
                break

    print("⏹ Recording stopped")
    # 3) concatenate into one array
    audio = np.concatenate(frames, axis=0)
    return audio.flatten()
async def main():
    fs = 24000
    audio_buffer = record_on_space(fs)
    pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
    audio_input = AudioInput(buffer=audio_buffer)

    print("⏳ Sending to CuratAI…")
    result = await pipeline.run(audio_input)

    print("▶️ Playing CuratAI’s response…")
    with sd.OutputStream(samplerate=fs, channels=1, dtype='int16') as player:
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                player.write(event.data)

if __name__ == "__main__":
    asyncio.run(main())

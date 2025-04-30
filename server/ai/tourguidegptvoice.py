import os
import sys
import joblib
import numpy as np
import asyncio
import argparse
import subprocess
import sounddevice as sd
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
from pydub import AudioSegment
from language_detector import LanguageDetector
import subprocess
from agents import Agent, function_tool
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from dotenv import load_dotenv
load_dotenv() 

import wave
import io
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
        f"Detect the language the user is asking in, use English If you can't detect the language or length of the query is less than 2. Please provide your answer entirely in that language fluently while maintaining the same level of detail and professionalism."
    )
    prompt = f"Context: {ctx}\n\nQuestion: {user_query}\nAnswer:"
    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": prompt}],
        max_tokens=1000
    )
    return resp.choices[0].message.content


@function_tool
async def rag_tool(query: str) -> str:
    return await rag_query(query)


agent = Agent(
    name="CuratAI",
    instructions=prompt_with_handoff_instructions(
        "You are CuratAI, the Met’s expert tour guide. "
        "Use the `rag_tool` to answer all visitor questions."
    ),
    model="gpt-4o-mini",
    tools=[rag_tool],
)
def decode_audio_bytes(raw_bytes: bytes, target_sr: int = 24000):
    """
    Decode the in-memory webm/other format bytes into a mono int16 numpy array.
    """
    # Write bytes to a pipe and call ffmpeg via subprocess
    p = subprocess.Popen(
        [
            "ffmpeg", "-i", "pipe:0",
            "-f", "s16le", "-acodec", "pcm_s16le",
            "-ac", "1", "-ar", str(target_sr),
            "pipe:1"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    out, _ = p.communicate(raw_bytes)
    buffer = np.frombuffer(out, dtype=np.int16)
    return buffer, target_sr

async def main():
    p = argparse.ArgumentParser(
        description="CuratAI voice pipeline (supports --stdin/--stdout streaming)"
    )
    p.add_argument("--stdin",  action="store_true",
                   help="Read the entire input audio from stdin.buffer")
    p.add_argument("--stdout", action="store_true",
                   help="Write the reply audio to stdout.buffer")
    p.add_argument("audio_path", nargs="?",
                   help="Path to audio file (if not using --stdin)")
    args = p.parse_args()

    # Load audio bytes
    if args.stdin:
        raw_audio = sys.stdin.buffer.read()
    else:
        if not args.audio_path or not os.path.isfile(args.audio_path):
            print("❌ Missing or invalid audio_path", file=sys.stderr)
            sys.exit(1)
        with open(args.audio_path, "rb") as f:
            raw_audio = f.read()

    # Decode into numpy PCM buffer
    audio_buffer, fs = decode_audio_bytes(raw_audio, target_sr=24000)

    # Run through voice pipeline
    pipeline    = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
    audio_input = AudioInput(buffer=audio_buffer)
    result      = await pipeline.run(audio_input)

    # Collect TTS bytes: assuming the pipeline yields raw PCM or wav bytes
    # Here we’ll accumulate all audio events
    tts_bytes = bytearray()
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            tts_bytes.extend(event.data)

    # Output
    if args.stdout:
        wav_buf = io.BytesIO()
        with wave.open(wav_buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs) 
            wf.writeframes(tts_bytes)
        wav_bytes = wav_buf.getvalue()
        sys.stdout.buffer.write(wav_bytes)
        sys.stdout.flush()
    
    else:
        # Fallback: save to file
        out_path = args.audio_path + ".reply.wav"
        with open(out_path, "wb") as f:
            f.write(tts_bytes)
        print("▶️ Written reply to", out_path)

if __name__ == "__main__":
    asyncio.run(main())
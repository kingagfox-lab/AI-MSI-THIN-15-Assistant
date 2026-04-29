import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("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")

# Inisialisasi memori chat
chat_history = []

app = FastAPI()

# Middleware CORS: Jembatan wajib agar HTML bisa akses Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    pesan: str

# API KEY OpenRouter kamu
OPENROUTER_API_KEY = "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"
@app.post("/chat/")
def ngobrol_dengan_ai(input_user: ChatInput):
    global chat_history
    try:
        chat_history.append({"role": "user", "content": input_user.pesan})
        
        if len(chat_history) > 3:
            chat_history = chat_history[-3:]

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Asisten Agung MSI",
            },
            data=json.dumps({
                # Coba pakai model Qwen, ini biasanya paling jarang error buat gratisan
                "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                "messages": [
                    {"role": "system", "content": "Kamu asisten Agung PPLG. Jawab singkat & Indonesia."}
                ] + chat_history
            })
        )
        
        hasil = response.json()

        # CEK DISINI: Kalau sukses
        if "choices" in hasil and len(hasil["choices"]) > 0:
            jawaban = hasil["choices"][0]["message"].get("content", "")
            chat_history.append({"role": "assistant", "content": jawaban})
            return {"jawaban_ai": jawaban}
        
        # CEK DISINI: Kalau gagal, kita bongkar error-nya
        else:
            chat_history = [] # Reset biar gak nyangkut
            error_msg = hasil.get("error", {}).get("message", "Gak tau kenapa, mungkin kuota habis.")
            return {"jawaban_ai": f"Duh Gung, OpenRouter bilang: {error_msg}"}

    except Exception as e:
        chat_history = []
        return {"jawaban_ai": f"Ada error teknis: {str(e)}"}
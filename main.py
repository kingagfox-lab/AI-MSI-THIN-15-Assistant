import os
import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 1. Load file .env dulu
load_dotenv()

# 2. Ambil kuncinya
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Cek di PowerShell saat startup
if OPENROUTER_API_KEY:
    print(f"--- STATUS: BERHASIL KONEK ---")
    print(f"Kunci Terdeteksi: {OPENROUTER_API_KEY[:10]}...")
else:
    print("--- STATUS: ERROR! KUNCI TIDAK ADA DI .ENV ---")

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

class ChatInput(BaseModel):
    pesan: str

@app.post("/chat/")
async def ngobrol_dengan_ai(input_user: ChatInput):
    global chat_history
    print(f"--- PESAN MASUK DARI HP: {input_user.pesan} ---")

    try:
        # Masukkan pesan user ke memori chat
        chat_history.append({"role": "user", "content": input_user.pesan})
        if len(chat_history) > 3:
            chat_history = chat_history[-3:]

        # Kirim ke OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/kingagfox-lab", # Link profilmu
                "X-Title": "Asisten Agung MSI",
            },
            data=json.dumps({
                "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
                "messages": [
                    {"role": "system", "content": "Kamu asisten Agung PPLG. Jawab singkat & Indonesia."}
                ] + chat_history
            })
        )
        
        hasil = response.json()

        if "choices" in hasil and len(hasil["choices"]) > 0:
            jawaban = hasil["choices"][0]["message"].get("content", "")
            chat_history.append({"role": "assistant", "content": jawaban})
            return {"jawaban_ai": jawaban}
        else:
            error_msg = hasil.get("error", {}).get("message", "Authentication Error")
            print(f"Log Error OpenRouter: {hasil}") # Muncul di PowerShell laptop
            return {"jawaban_ai": f"Duh Gung, ada masalah: {error_msg}"}

    except Exception as e:
        print(f"Error Teknis: {str(e)}")
        return {"jawaban_ai": f"Ada error teknis: {str(e)}"}

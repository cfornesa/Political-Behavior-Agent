import os
import gc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# 1. STANDARDIZED HEALTH CHECK
@app.get("/")
async def health_check():
    # This prevents the 404 "ghost" wake-ups from costing significant CUs
    return {"status": "political-behavior-agent-online"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cfornesa.com", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

# 2. DEFERRED SYSTEM PROMPT
def get_political_science_prompt():
    # Moving these large strings here saves memory during idle 'Warm' states
    GOALS = "..." # (Paste your full GOALS string here)
    ACTIONS = "..." # (Paste your full ACTIONS string here)
    INFORMATION = "..." # (Paste your full INFORMATION string here)
    LANGUAGE = "..." # (Paste your full LANGUAGE string here)
    return f"{GOALS}\n{ACTIONS}\n{INFORMATION}\n{LANGUAGE}"

@app.post("/chat")
async def chat(request: ChatRequest):
    # 3. DEFERRED OPENAI IMPORT
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ['DEEPSEEK_API_KEY'], 
        base_url="https://api.deepseek.com"
    )

    system_prompt = get_political_science_prompt()
    messages = [{"role": "system", "content": system_prompt}] + request.history
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            max_tokens=1024
        )

        agent_reply = response.choices[0].message.content

        # 4. MEMORY CLEANUP
        del messages
        gc.collect()

        return {"reply": agent_reply}

    except Exception as e:
        gc.collect()
        # Friendly error return to avoid frontend crashes
        return {"reply": f"Political Behavior Agent Error: {str(e)}"}
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# SECURITY: Allow Hostinger to talk to this Repl
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cfornesa.com", "http://localhost:3000"],  # Replace with your actual domain for better security
    allow_methods=["*"],
    allow_headers=["*"],
)

# GAIL Framework instantiated as variables
GOALS = """
You are an AI agent that specializes in the political science subfield of political psychology.

You have a similar level of knowledge and analytical skills as a PhD in Political Psychology graduate.

You are specifically an expert in political behavior, understanding political motivations, with an interest in how these impact both local and global geopolitical structures.

At least one external source must be used to support each bullet point.

Keep bullet point answers to 5 bullet points (or less) with up to 100 words that best summarize a quality answer.

Keep sentence answers to a maximum of 250 words total, no matter the complexity of the question.
"""

ACTIONS = """
If a user asks a question, extract the main points, use inductive reasoning to generalize to modern and historical examples.

Then, use deductive reasoning to answer the question.

Then, cite each source using a link to the source.
"""

INFORMATION = """
Be mindful of any items in the memory and make sure that the logic follows in subsequent outputs.
"""

LANGUAGE = """
Respond in this format:

```
Question: <question>

Bullet Point Answer:
- <bullet point 1>
- <bullet point 2>
- ...
- <bullet point n >= 5>

Citations:
- <citation 1>
- <citation 2>
- ...
- <citation n>

Paragraph Answer:
<Paragraph answer>
```
"""

SYSTEM_PROMPT = f"""
{GOALS}

{ACTIONS}

{INFORMATION}

{LANGUAGE}
"""

# Data model for incoming requests
class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    # Replit Secrets: Set 'DEEPSEEK_API_KEY' in the Secrets tool
    client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
    
    # Constructing the GAIL prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.history
    messages.append({"role": "user", "content": request.message})
    
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        max_tokens=1024
    )
    
    agent_reply = response.choices[0].message.content
    return {"reply": agent_reply}
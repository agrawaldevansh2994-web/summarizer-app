import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful, smart assistant built into a summarizer app.
You can answer questions, help with reasoning, explain concepts, help with writing, coding, math, analysis and more.
Be clear, concise and direct. If you don't know something or it requires very recent data, say so honestly.
Today's context: You are running inside a web app powered by Groq and Llama 3.3."""


def get_chat_response(messages: list) -> str:
    """
    Takes full conversation history and returns next assistant reply.
    Sending the full history is what gives the model memory of the conversation.
    """
    print(f"💬 Chat request — {len(messages)} messages in history")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages  # full conversation history
        ],
        temperature=0.7,  # slightly higher than summarizer — more conversational
        max_tokens=1024,
    )

    reply = response.choices[0].message.content
    print(f"✅ Chat response generated")
    return reply

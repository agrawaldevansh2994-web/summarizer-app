import os
import fitz  # PyMuPDF
from groq import Groq

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key=os.getenv(
    "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"))
MODEL = "llama-3.3-70b-versatile"


# ── Extract text from PDF ─────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        print(f"📄 PDF opened — {len(doc)} pages found")
        full_text = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
                print(f"   ✅ Page {page_num + 1} extracted")
        doc.close()

        if not full_text:
            raise ValueError("No text found. The PDF may be a scanned image.")

        print(f"📝 Total text extracted: {len(' '.join(full_text).split())} words")
        return "\n\n".join(full_text)

    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")


# ── Summarize with Groq ───────────────────────────────────────────────────────
def summarize_pdf_text(text: str, style: str = "bullet") -> str:
    style_prompts = {
        "bullet": "Summarize this document in clear bullet points.",
        "paragraph": "Write a concise 2-3 paragraph summary of this document.",
        "tldr": "Give a single TL;DR sentence summarizing the document.",
    }
    instruction = style_prompts.get(style, style_prompts["bullet"])

    MAX_WORDS = 6000
    words = text.split()
    if len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS]) + "\n\n[Document truncated]"

    print(f"🤖 Sending to Groq (llama3)...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes documents. Be clear and accurate."
            },
            {
                "role": "user",
                "content": f"{instruction}\n\nDocument:\n{text}"
            }
        ],
        temperature=0.3,
    )
    print(f"✅ Groq responded!")
    return response.choices[0].message.content


# ── Main function called by the router ───────────────────────────────────────
def summarize_pdf(file_bytes: bytes, filename: str, style: str = "bullet") -> dict:
    text = extract_text_from_pdf(file_bytes)
    summary = summarize_pdf_text(text, style)
    return {
        "filename": filename,
        "word_count": len(text.split()),
        "summary": summary,
        "style": style,
    }

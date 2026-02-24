import re
import os
import yt_dlp
from groq import Groq

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


# ── Extract video ID from any YouTube URL format ──────────────────────────────
def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"shorts\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


# ── Fetch transcript using yt-dlp ─────────────────────────────────────────────
def fetch_transcript(video_id: str) -> str:
    print(f"🎬 Fetching transcript for video: {video_id}")
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "skip_download": True,          # don't download the video
        "writesubtitles": True,         # get subtitles
        "writeautomaticsub": True,      # get auto-generated subtitles too
        "subtitleslangs": ["en"],       # English only
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Try manual subtitles first, then auto-generated
            subtitles = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})

            chosen = subtitles.get("en") or auto_subs.get("en")

            if not chosen:
                raise ValueError("No English captions found for this video.")

            # Get the JSON format subtitle
            json_sub = next(
                (s for s in chosen if s.get("ext") == "json3"), None)
            if not json_sub:
                json_sub = chosen[0]

            # Download the subtitle content
            import urllib.request
            with urllib.request.urlopen(json_sub["url"]) as response:
                import json
                data = json.loads(response.read().decode())

            # Extract text from JSON3 format
            texts = []
            for event in data.get("events", []):
                for seg in event.get("segs", []):
                    t = seg.get("utf8", "").strip()
                    if t and t != "\n":
                        texts.append(t)

            full_text = " ".join(texts)

            if not full_text.strip():
                raise ValueError("Transcript was empty.")

            print(f"✅ Transcript fetched: {len(full_text.split())} words")
            return full_text

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {str(e)}")


# ── Summarize with Groq ───────────────────────────────────────────────────────
def summarize_text(text: str, style: str = "bullet") -> str:
    style_prompts = {
        "bullet": "Summarize this in clear bullet points covering the key ideas.",
        "paragraph": "Write a concise 2-3 paragraph summary of this content.",
        "tldr": "Give a single TL;DR sentence summarizing the main point.",
    }
    instruction = style_prompts.get(style, style_prompts["bullet"])

    MAX_WORDS = 6000
    words = text.split()
    if len(words) > MAX_WORDS:
        text = " ".join(words[:MAX_WORDS]) + "\n\n[Transcript truncated]"

    print(f"🤖 Sending to Groq (llama3)...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes YouTube video transcripts. Be clear and concise."
            },
            {
                "role": "user",
                "content": f"{instruction}\n\nTranscript:\n{text}"
            }
        ],
        temperature=0.3,
    )
    print(f"✅ Groq responded!")
    return response.choices[0].message.content


# ── Main function called by the router ───────────────────────────────────────
def summarize_youtube_video(url: str, style: str = "bullet") -> dict:
    video_id = extract_video_id(url)
    transcript = fetch_transcript(video_id)
    summary = summarize_text(transcript, style)
    return {
        "video_id": video_id,
        "transcript_length": len(transcript.split()),
        "summary": summary,
        "style": style,
    }

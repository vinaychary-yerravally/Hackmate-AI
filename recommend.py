import os

from dotenv import load_dotenv
from google import genai

# Load GEMINI_API_KEY (and optional model config) from a local .env file.
load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"

# Ordered list of models to try. The first is the primary, the rest are
# fallbacks used when a model is overloaded (503) or unavailable.
def _model_chain():
    primary = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    fallbacks = [
        m.strip()
        for m in os.getenv("GEMINI_MODEL_FALLBACKS", "").split(",")
        if m.strip()
    ]
    chain = [primary] + fallbacks
    # De-duplicate while preserving order.
    seen, ordered = set(), []
    for m in chain:
        if m and m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


client = None
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:  # noqa: BLE001 - surface any init failure as no-client
        print(f"Client Init Error: {e}")


def is_greeting(text: str) -> bool:
    clean = text.strip().lower().strip("!.,?")
    greetings = [
        "hi", "hello", "hey", "hola", "good morning", "good evening",
        "who are you", "hi there", "hey there",
    ]
    return clean in greetings or len(clean) <= 3


def _generate(prompt: str) -> str:
    """Send a prompt to Gemini, trying each configured model until one works."""
    last_error = None
    for model in _model_chain():
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if text:
                return text
            last_error = "empty response"
        except Exception as e:  # noqa: BLE001 - try the next model
            last_error = f"{type(e).__name__}: {e}"
    raise RuntimeError(last_error or "no models configured")


def recommend_problems(user_idea: str, top_n: int = 5):
    clean_query = user_idea.strip()
    if not clean_query:
        return [], ""

    if not client:
        return [], (
            "⚠️ Gemini API key not configured. Add GEMINI_API_KEY to the "
            ".env file (see .env) and restart the app."
        )

    # 1. Handle conversational greetings.
    if is_greeting(clean_query):
        try:
            return [], _generate(
                f"User said: '{clean_query}'. Reply warmly and concisely as "
                "HackMate AI, an official Smart India Hackathon AI mentor. Ask "
                "them what project idea or domain they want to explore today. "
                "Do not mention Gemini or Google."
            )
        except Exception:
            return [], (
                "Hello! I am HackMate AI, your Smart India Hackathon mentor. "
                "What project idea are you exploring today?"
            )

    # 2. Direct AI generation.
    prompt = f"""
    You are HackMate AI, an expert mentor for Smart India Hackathon (SIH) teams.
    Never mention Gemini, Google, or LLMs in your response. Speak strictly as HackMate AI.

    User Query / Project Idea: "{clean_query}"

    Instructions:
    1. **Recommended SIH Problem Statements:** Suggest {top_n} realistic Smart India Hackathon problem statements (including a plausible PS ID, Title, Theme, and Organization) that best align with their idea.
    2. **Project Fit & Relevance:** Explain why these problem statement themes match their project idea.
    3. **Key MVP Features:** List essential features they should build for an impressive hackathon prototype.
    4. **Recommended Tech Stack:** Suggest a modern, production-ready stack (Frontend, Backend, AI/ML models, and Database).
    """

    try:
        return [], _generate(prompt)
    except Exception as e:  # noqa: BLE001
        return [], f"❌ Error: {e}"

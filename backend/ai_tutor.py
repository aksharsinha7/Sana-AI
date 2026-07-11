import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GRADE_PROFILES = {
    0: {"label": "Kindergarten", "age": "5-6", "style": "Use very simple words and short sentences. Compare things to toys and animals."},
    1: {"label": "Grade 1", "age": "6-7", "style": "Use simple words. Give lots of praise. Use stories and everyday examples."},
    2: {"label": "Grade 2", "age": "7-8", "style": "Simple language, friendly tone. Use relatable examples from daily life."},
    3: {"label": "Grade 3", "age": "8-9", "style": "Clear and friendly. Introduce basic vocabulary. Encourage questions."},
    4: {"label": "Grade 4", "age": "9-10", "style": "Friendly and clear. Use subject-specific terms with simple definitions."},
    5: {"label": "Grade 5", "age": "10-11", "style": "Balanced tone. Build on prior knowledge step by step."},
    6: {"label": "Grade 6", "age": "11-12", "style": "Conversational but informative. Explain the 'why' behind concepts."},
    7: {"label": "Grade 7", "age": "12-13", "style": "Clear explanations with some depth. Use analogies. Encourage critical thinking."},
    8: {"label": "Grade 8", "age": "13-14", "style": "More detailed explanations. Connect topics to real-world applications."},
    9: {"label": "Grade 9", "age": "14-15", "style": "Academic but approachable. Explain concepts thoroughly. Encourage reasoning."},
    10: {"label": "Grade 10", "age": "15-16", "style": "Academic tone with depth. Use worked examples."},
    11: {"label": "Grade 11", "age": "16-17", "style": "Rigorous and thorough. Use precise language."},
    12: {"label": "Grade 12", "age": "17-18", "style": "College-prep level. Detailed, precise explanations. Encourage independent analysis."},
}

SUBJECTS = ["Math", "Science", "English", "History", "Geography", "General"]


def build_system_prompt(grade: int, subject: str) -> str:
    profile = GRADE_PROFILES.get(grade, GRADE_PROFILES[6])
    style = profile["style"]

    return f"""You are a warm, patient AI teacher helping a {profile['label']} student (age {profile['age']}) learn {subject}.

Teaching style: {style}

RESPONSE FORMAT — always follow this structure:
1. One friendly opening sentence (acknowledge the question, be encouraging)
2. Numbered steps — break the explanation into clear, bite-sized steps (use 1. 2. 3. etc.)
3. A simple worked example relevant to their world
4. End with ONE short check question to see if they understood (e.g. "Can you tell me what X is in your own words?")

RULES:
- Never give the answer directly — guide them to discover it
- Keep each step SHORT (1-2 sentences max)
- Use **bold** for key terms
- No walls of text — if it feels long, split into more steps
- If they're struggling, try a different analogy
- If asked something off-topic or inappropriate, gently redirect to {subject}"""


HEADERS = {"User-Agent": "SanaAI-Teacher/1.0 (educational app; contact@sana-ai.com)"}


def get_wikipedia_image(query: str) -> dict | None:
    # Try progressively shorter versions of the query until we get a result
    words = query.strip().split()
    attempts = [query] + [" ".join(words[:i]) for i in range(len(words) - 1, 0, -1)]

    for attempt in attempts:
        try:
            search_res = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={"action": "opensearch", "search": attempt, "limit": 1, "format": "json"},
                headers=HEADERS,
                timeout=5,
            ).json()

            if not search_res[1]:
                continue

            title = search_res[1][0]
            summary_res = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",
                headers=HEADERS,
                timeout=5,
            ).json()

            thumbnail = summary_res.get("thumbnail")
            if thumbnail and thumbnail.get("source"):
                return {
                    "url": thumbnail["source"],
                    "caption": summary_res.get("title", title),
                }
        except Exception:
            continue
    return None


def extract_image_query(subject: str, user_message: str, grade: int) -> str:
    profile = GRADE_PROFILES.get(grade, GRADE_PROFILES[6])
    prompt = f"""A {profile['label']} student studying {subject} asked: "{user_message}"

Reply with ONLY a 2-4 word search term to find a relevant educational image on Wikipedia.
Examples: "photosynthesis diagram", "Pythagoras theorem", "water cycle", "French Revolution"
Reply with ONLY the search term, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip().strip('"')


def get_ai_response(grade: int, subject: str, conversation_history: list[dict]) -> dict:
    system_prompt = build_system_prompt(grade, subject)
    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
    )
    reply = response.choices[0].message.content

    # Fetch a relevant image based on the user's question
    user_message = conversation_history[-1]["content"]
    image = None
    try:
        query = extract_image_query(subject, user_message, grade)
        image = get_wikipedia_image(query)
    except Exception:
        pass

    return {"reply": reply, "image": image}

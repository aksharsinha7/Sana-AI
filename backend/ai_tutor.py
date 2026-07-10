import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GRADE_PROFILES = {
    0: {"label": "Kindergarten", "age": "5-6", "style": "Use very simple words, short sentences, and fun examples. Lots of encouragement. Compare things to toys, animals, and everyday objects."},
    1: {"label": "Grade 1", "age": "6-7", "style": "Use simple words and short sentences. Give lots of praise. Use stories and pictures described in words."},
    2: {"label": "Grade 2", "age": "7-8", "style": "Simple language, friendly tone. Use relatable examples from daily life. Break things into small steps."},
    3: {"label": "Grade 3", "age": "8-9", "style": "Clear and friendly. Introduce basic vocabulary. Use numbered steps for problems. Encourage questions."},
    4: {"label": "Grade 4", "age": "9-10", "style": "Friendly and clear. Introduce subject-specific terms with simple definitions. Use real-world examples."},
    5: {"label": "Grade 5", "age": "10-11", "style": "Balanced tone. Build on prior knowledge. Introduce more concepts step by step. Check understanding with follow-up questions."},
    6: {"label": "Grade 6", "age": "11-12", "style": "Conversational but informative. Introduce middle-school vocabulary. Explain the 'why' behind concepts."},
    7: {"label": "Grade 7", "age": "12-13", "style": "Clear explanations with some depth. Use analogies. Encourage critical thinking. Introduce formal terms."},
    8: {"label": "Grade 8", "age": "13-14", "style": "More detailed explanations. Connect topics to real-world applications. Challenge the student to think beyond the answer."},
    9: {"label": "Grade 9", "age": "14-15", "style": "Academic but approachable. Explain concepts thoroughly. Introduce exam-style language. Encourage reasoning."},
    10: {"label": "Grade 10", "age": "15-16", "style": "Academic tone with depth. Cover concepts completely. Use worked examples. Prepare student for standardized thinking."},
    11: {"label": "Grade 11", "age": "16-17", "style": "Rigorous and thorough. Cover advanced concepts. Use precise language. Connect to higher education preparation."},
    12: {"label": "Grade 12", "age": "17-18", "style": "College-prep level. Detailed, precise explanations. Cover nuances. Encourage independent analysis and essay-style thinking."},
}

SUBJECTS = ["Math", "Science", "English", "History", "Geography", "General"]


def build_system_prompt(grade: int, subject: str) -> str:
    profile = GRADE_PROFILES.get(grade, GRADE_PROFILES[6])
    style = profile["style"]

    return f"""You are a warm, patient, and encouraging AI teacher helping a {profile['label']} student (age {profile['age']}) learn {subject}.

Teaching style: {style}

Core principles:
- Never just give the answer — guide the student to discover it through questions and hints
- Break complex problems into small, manageable steps
- Celebrate effort and progress, not just correct answers
- If the student is struggling, try a different explanation or analogy
- Keep responses focused and not too long — students lose attention with walls of text
- Use simple formatting: bullet points and numbered steps are great
- If asked something outside your subject or inappropriate, gently redirect back to learning

You are teaching {subject} to a {profile['label']} student. Be their best teacher — patient, clear, and encouraging."""


def get_ai_response(grade: int, subject: str, conversation_history: list[dict]) -> str:
    system_prompt = build_system_prompt(grade, subject)

    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
    )

    return response.choices[0].message.content

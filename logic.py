import json
import os
import random

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "questions.json")

def load_questions(difficulty: str) -> list[dict]:
    """Load questions from JSON file for given difficulty."""
    try:
        with open(QUESTIONS_FILE, "r") as f:
            data = json.load(f)
        questions = data.get(difficulty.lower(), [])
        shuffled = questions.copy()
        random.shuffle(shuffled)
        return shuffled
    except FileNotFoundError:
        raise FileNotFoundError(f"Questions file not found: {QUESTIONS_FILE}")
    except json.JSONDecodeError:
        raise ValueError("Corrupted questions file.")

def check_answer(question: dict, selected: str) -> bool:
    """Check if the selected answer is correct."""
    return selected.strip() == question["answer"].strip()

def calculate_score(correct: int, total: int) -> dict:
    """Calculate score and grade."""
    percentage = (correct / total * 100) if total > 0 else 0
    if percentage >= 80:
        grade = "Excellent! 🏆"
        color = "#00e676"
    elif percentage >= 60:
        grade = "Good Job! 👍"
        color = "#ffeb3b"
    elif percentage >= 40:
        grade = "Keep Practicing! 📚"
        color = "#ff9800"
    else:
        grade = "Try Again! 💪"
        color = "#f44336"
    return {
        "correct": correct,
        "total": total,
        "percentage": round(percentage, 1),
        "grade": grade,
        "color": color
    }

def get_difficulty_config(difficulty: str) -> dict:
    """Return styling config per difficulty."""
    configs = {
        "easy":   {"color": "#00e676", "emoji": "🟢", "label": "EASY",   "time": 30},
        "medium": {"color": "#ffeb3b", "emoji": "🟡", "label": "MEDIUM", "time": 20},
        "hard":   {"color": "#f44336", "emoji": "🔴", "label": "HARD",   "time": 15},
    }
    return configs.get(difficulty.lower(), configs["easy"])
import pytest
from logic import load_questions, check_answer, calculate_score, get_difficulty_config


# ─── load_questions ───────────────────────────────────────────────────────────

def test_load_questions_easy():
    questions = load_questions("easy")
    assert isinstance(questions, list)
    assert len(questions) > 0

def test_load_questions_medium():
    questions = load_questions("medium")
    assert isinstance(questions, list)
    assert len(questions) > 0

def test_load_questions_hard():
    questions = load_questions("hard")
    assert isinstance(questions, list)
    assert len(questions) > 0

def test_load_questions_structure():
    questions = load_questions("easy")
    for q in questions:
        assert "question" in q
        assert "options" in q
        assert "answer" in q
        assert isinstance(q["options"], list)
        assert len(q["options"]) == 4
        assert q["answer"] in q["options"]

def test_load_questions_invalid_difficulty():
    questions = load_questions("unknown_level")
    assert questions == []

def test_load_questions_case_insensitive():
    q1 = load_questions("Easy")
    q2 = load_questions("easy")
    # Same questions (though shuffled differently)
    assert len(q1) == len(q2)


# ─── check_answer ─────────────────────────────────────────────────────────────

def test_check_answer_correct():
    q = {"question": "What is 2+2?", "options": ["3", "4", "5", "6"], "answer": "4"}
    assert check_answer(q, "4") is True

def test_check_answer_wrong():
    q = {"question": "What is 2+2?", "options": ["3", "4", "5", "6"], "answer": "4"}
    assert check_answer(q, "3") is False

def test_check_answer_with_whitespace():
    q = {"question": "Capital of France?", "options": ["Paris", "Berlin"], "answer": "Paris"}
    assert check_answer(q, "  Paris  ") is True

def test_check_answer_empty_string():
    q = {"question": "Q?", "options": ["A", "B"], "answer": "A"}
    assert check_answer(q, "") is False

def test_check_answer_case_sensitive():
    q = {"question": "Q?", "options": ["yes", "no"], "answer": "yes"}
    assert check_answer(q, "Yes") is False


# ─── calculate_score ──────────────────────────────────────────────────────────

def test_calculate_score_perfect():
    result = calculate_score(10, 10)
    assert result["percentage"] == 100.0
    assert result["correct"] == 10
    assert result["total"] == 10
    assert "Excellent" in result["grade"]

def test_calculate_score_zero():
    result = calculate_score(0, 10)
    assert result["percentage"] == 0.0
    assert "Try Again" in result["grade"]

def test_calculate_score_good():
    result = calculate_score(7, 10)
    assert result["percentage"] == 70.0
    assert "Good" in result["grade"]

def test_calculate_score_medium_range():
    result = calculate_score(5, 10)
    assert result["percentage"] == 50.0
    assert "Keep" in result["grade"]

def test_calculate_score_zero_total():
    result = calculate_score(0, 0)
    assert result["percentage"] == 0.0

def test_calculate_score_has_color():
    result = calculate_score(8, 10)
    assert "color" in result
    assert result["color"].startswith("#")

def test_calculate_score_partial():
    result = calculate_score(3, 7)
    assert round(result["percentage"], 1) == round(3 / 7 * 100, 1)


# ─── get_difficulty_config ────────────────────────────────────────────────────

def test_difficulty_config_easy():
    config = get_difficulty_config("easy")
    assert config["label"] == "EASY"
    assert config["time"] == 30
    assert "color" in config
    assert "emoji" in config

def test_difficulty_config_medium():
    config = get_difficulty_config("medium")
    assert config["label"] == "MEDIUM"
    assert config["time"] == 20

def test_difficulty_config_hard():
    config = get_difficulty_config("hard")
    assert config["label"] == "HARD"
    assert config["time"] == 15

def test_difficulty_config_case_insensitive():
    c1 = get_difficulty_config("HARD")
    c2 = get_difficulty_config("hard")
    assert c1 == c2

def test_difficulty_config_unknown_falls_back():
    config = get_difficulty_config("unknown")
    assert "color" in config
    assert "time" in config
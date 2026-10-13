import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch


os.environ.setdefault("ASI_API_KEY", "test-key")
os.environ.setdefault("TUTOR_AGENT_ADDRESS", "agent1tutor")
os.environ.setdefault("QUIZ_AGENT_ADDRESS", "agent1quiz")
os.environ.setdefault("EVALUATOR_AGENT_ADDRESS", "agent1evaluator")

import evaluator_agent
import quiz_creator_agent
import tutor_agent


def model_response(content):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class AnswerParsingTests(unittest.TestCase):
    def test_accepts_common_answer_formats(self):
        expected = {1: "A", 2: "C", 3: "B"}
        self.assertEqual(evaluator_agent.parse_answers("A, C, B"), expected)
        self.assertEqual(evaluator_agent.parse_answers("A C B"), expected)
        self.assertEqual(evaluator_agent.parse_answers("1:A 2:C 3:B"), expected)
        self.assertEqual(evaluator_agent.parse_answers("'A, C, B'"), expected)
        self.assertEqual(
            evaluator_agent.parse_answers("@study-tutor `A, C, B`"),
            expected,
        )

    def test_rejects_incomplete_numbered_answers(self):
        with self.assertRaises(ValueError):
            evaluator_agent.parse_answers("1:A, 3:B")

    def test_rejects_duplicate_numbered_answers(self):
        with self.assertRaises(ValueError):
            evaluator_agent.parse_answers("1:A, 1:B, 2:C, 3:D")


class QuizValidationTests(unittest.TestCase):
    def test_extracts_json_from_markdown(self):
        raw = 'Result:\n```json\n{"questions": []}\n```'
        self.assertEqual(
            quiz_creator_agent.parse_json_object(raw),
            {"questions": []},
        )

    def test_creates_validated_quiz(self):
        payload = {
            "questions": [
                {
                    "question": f"Question {number}?",
                    "options": {
                        "A": "First",
                        "B": "Second",
                        "C": "Third",
                        "D": "Fourth",
                    },
                    "answer": "A",
                    "explanation": "First is correct.",
                }
                for number in range(1, 4)
            ]
        }
        with patch.object(
            quiz_creator_agent.client.chat.completions,
            "create",
            return_value=model_response(json.dumps(payload)),
        ):
            questions, answer_key = quiz_creator_agent.create_quiz(
                "A topic",
                "A short factual lesson.",
            )

        self.assertIn("1. Question 1?", questions)
        self.assertEqual(len(json.loads(answer_key)), 3)


class TutorInputTests(unittest.TestCase):
    def test_accepts_command_and_natural_topic(self):
        self.assertEqual(
            tutor_agent.topic_from_message("topic: Neural networks"),
            "Neural networks",
        )
        self.assertEqual(
            tutor_agent.topic_from_message("Explain neural networks"),
            "Explain neural networks",
        )

    def test_extracts_quoted_topic_from_asi_request(self):
        request = (
            '@study-tutor Run a complete AI Study Mission on the topic '
            '"Overfitting in Machine Learning".\n\n'
            "Explain it and send the lesson to the Quiz Creator Agent."
        )
        self.assertEqual(
            tutor_agent.topic_from_message(request),
            "Overfitting in Machine Learning",
        )

    def test_removes_leading_agent_mention(self):
        self.assertEqual(
            tutor_agent.normalize_student_text("@study-tutor status"),
            "status",
        )

    def test_distinguishes_new_mission_from_quiz_answers(self):
        request = (
            '@study-tutor Run a complete AI Study Mission on the topic '
            '"Overfitting in Machine Learning".'
        )
        self.assertTrue(tutor_agent.looks_like_topic_request(request))
        self.assertFalse(tutor_agent.looks_like_topic_request("'A, C, B'"))


if __name__ == "__main__":
    unittest.main()

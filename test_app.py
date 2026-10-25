import unittest
from unittest.mock import patch

from app import app
from recommend import recommend_problems


class TestHackMatchAI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_homepage_load(self):
        """Verify homepage loads with HTTP 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @patch("recommend.client")
    @patch("recommend._generate")
    def test_recommendation_logic(self, mock_generate, mock_client):
        """Verify recommendation engine logic using a mocked model response."""
        mock_generate.return_value = "Mocked AI Strategic Advice for Testing"

        recs, advice = recommend_problems(
            "Smart Agriculture crop disease detection using AI"
        )

        self.assertIsInstance(recs, list)
        self.assertEqual(advice, "Mocked AI Strategic Advice for Testing")
        mock_generate.assert_called_once()

    @patch("recommend.client")
    @patch("recommend._generate")
    def test_greeting_branch(self, mock_generate, mock_client):
        """Greetings return no recommendations, just a chat reply."""
        mock_generate.return_value = "Hi there! What would you like to build?"

        recs, advice = recommend_problems("hello")

        self.assertEqual(recs, [])
        self.assertIn("Hi there!", advice)

    @patch("recommend.client", None)
    def test_missing_key_is_handled(self):
        """With no client configured, a friendly message is returned."""
        recs, advice = recommend_problems("AI crop disease detection")
        self.assertEqual(recs, [])
        self.assertIn("GEMINI_API_KEY", advice)

    @patch("app.recommend_problems")
    def test_form_submission_route(self, mock_recommend):
        """Verify POST handling renders the model advice with HTTP 200."""
        mock_recommend.return_value = ([], "Mocked AI Strategic Advice for Testing")

        response = self.client.post(
            "/", data={"project_idea": "Blockchain invoice verification for MSME"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Mocked AI Strategic Advice", response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)

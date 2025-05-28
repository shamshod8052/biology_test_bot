from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import BaseDiagnosticTest, BaseAnswer

User = get_user_model()

class BaseDiagnosticTestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.test = BaseDiagnosticTest.objects.create(name="Sample Test", file="documents/murojaatlar.xls")

        # 2 ta savol: biri CLOSE, biri OPEN
        BaseAnswer.objects.create(test=self.test, type=BaseAnswer.Type.CLOSE, value='A')
        BaseAnswer.objects.create(test=self.test, type=BaseAnswer.Type.OPEN, value='Open Answer')

    def test_chunk_answers_valid_input(self):
        text = "AaAnswer for open\nExtra"
        result = self.test.parse_user_answers(text)
        self.assertEqual(result, ['A', 'Extra'])

    def test_chunk_answers_empty_lines_ignored(self):
        text = "\n\nA\n\nOpen answer\n\n"
        result = self.test.parse_user_answers(text)
        self.assertEqual(result, ['A', 'Open answer'])

    def test_validate_answers_correct(self):
        answers = ['A', 'Open answer']
        try:
            self.test._validate_answers(answers)
        except ValidationError:
            self.fail("_validate_answers() raised ValidationError unexpectedly!")

    def test_validate_answers_incorrect_length(self):
        with self.assertRaises(ValidationError):
            self.test._validate_answers(['Only one'])

    def test_add_answers_creates_user_answer(self):
        answers_text = "A\nOpen"
        self.test.add_user_answers(self.user, answers_text)
        self.assertTrue(self.test.is_answered(self.user))
        user_answer = self.test.get_user_answer_text(self.user)
        self.assertIn("Your answers", user_answer)

    def test_add_answers_invalid_data(self):
        answers_text = "Only one line"
        with self.assertRaises(ValidationError):
            self.test.add_user_answers(self.user, answers_text)

    def test_get_user_answer_text_none(self):
        self.assertIsNone(self.test.get_user_answer_text(self.user))

    def test_add_answers_invalid_data2(self):
        answers_text = "abc"
        with self.assertRaises(ValidationError):
            self.test.add_user_answers(self.user, answers_text)

from ragcore.models.prompt_model import PromptGenerator


class TestPromptGenerator:
    def test_get_prompt(self):
        model = PromptGenerator()
        prompt = model.get_prompt("What a question here?", "Context a, context b")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

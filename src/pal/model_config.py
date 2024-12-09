from transformers import AutoTokenizer


class ModelConfig:

    def __init__(self, model: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model)

        if self.tokenizer.chat_template is not None:
            self.template_source = self.tokenizer.chat_template
        else:
            self.template_source = open("src/pal/chat_templates/chatml.jinja").read()

        if self.tokenizer.eos_token is not None:
            self.stop_strings = [self.tokenizer.eos_token]
        else:
            self.stop_strings = ["<|im_end|>"]

    def template(self, **kwargs):
        return self.tokenizer.apply_chat_template(
            tokenize=False, add_generation_prompt=True, **kwargs
        )

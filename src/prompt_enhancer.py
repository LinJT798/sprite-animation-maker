import json
from openai import OpenAI

class PromptEnhancer:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.client = OpenAI()
        
    def enhance(self, user_input):
        """使用GPT-4.1润色用户输入的提示词"""
        template = self.config['prompt_enhancement']['template']
        prompt = template.format(user_input=user_input)
        
        response = self.client.responses.create(
            model=self.config['prompt_enhancement']['model'],
            input=prompt
        )
        
        return response.output_text
from typing import List, Callable


class PromptOption:
    def __init__(self, key: str, desc: str, action: Callable):
        self.key: str = key
        self.desc: str = desc
        self.action: Callable = action


class Prompt:

    @staticmethod
    def show_prompt_yes_no(text: str, yes_action: Callable, no_action: Callable):
        print("This is a yes/no prompt.")
        pass

    @staticmethod
    def show_prompt(text: str, options: List[PromptOption]):
        pass

    @staticmethod
    def show_prompt_text_input(text: str):
        pass

    @staticmethod
    def get_input():
        pass

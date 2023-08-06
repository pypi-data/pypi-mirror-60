from typing import List, Callable, Dict
import kix
from kix.color import Color


class PromptOption:
    def __init__(self, key: str, desc: str, action: Callable):
        self.key: str = key
        self.desc: str = desc
        self.action: Callable = action


class Prompt:

    MOCK_INPUT_LOADED_VALUE = []

    @staticmethod
    def strip_special_characters(text: str):
        return text.strip("/.\n\r\t ")

    @staticmethod
    def decorate_with_header(text: str):
        prompt_header = kix.green("[INPUT]")
        return f"{prompt_header} {text}"

    @staticmethod
    def show_yes_no(text: str) -> bool:

        yes_set = {"y", "yes"}
        no_set = {"n", "n"}

        while True:

            # Modify prompt.
            modified_prompt = f"{Prompt.decorate_with_header(text)} [y/n]: "

            # Show prompt.
            x = Prompt.get_input(modified_prompt)

            # Validate.
            if x.lower() in yes_set:
                return True

            if x.lower() in no_set:
                return False

            # Failed to read. Try again.
            kix.log.warning(f"Unable to read input '{x}'. Must be one of [y/n]. Please try again.\n")

    @staticmethod
    def show_options(text: str, options: List[PromptOption]):

        # Show the heading.
        heading = kix.green(text)

        # Show options.
        options_map_display = {x.key: x.desc for x in options}
        options_map: Dict[str, PromptOption] = {x.key: x for x in options}

        lines = kix.expand(heading, options_map_display, stem_color=Color.GREEN)
        for line in lines:
            print(line)

        # Show prompt.
        while True:
            prompt_text = Prompt.decorate_with_header("Please select an option: ")
            x = Prompt.get_input(prompt_text)

            if x in options_map:

                option = options_map[x]
                feedback = Prompt.decorate_with_header(kix.green(f"Received {x} : {option.desc}"))
                print(feedback)
                option.action()
                return

            else:
                prompt_options = [k for k in options_map.keys()]
                prompt_options_text = f"[{'|'.join(prompt_options)}]"
                kix.log.warning(f"Unable to read input '{x}'. "
                                f"Must be one of {prompt_options_text}. "
                                f"Please try again.\n")

    @staticmethod
    def show_text_input(text: str):
        # Show the prompt
        modified_prompt = Prompt.decorate_with_header(f"{text}: ")
        x = Prompt.get_input(modified_prompt)
        feedback = Prompt.decorate_with_header(kix.green(f"Received: {x}"))
        print(feedback)
        return x

    @staticmethod
    def get_input(prompt: str) -> str:

        # Mock the input for testing.
        if len(Prompt.MOCK_INPUT_LOADED_VALUE) > 0:
            return_value = Prompt.MOCK_INPUT_LOADED_VALUE[0]
            print(f"{prompt} {return_value}")
            Prompt.MOCK_INPUT_LOADED_VALUE.pop(0)
            return return_value

        # Not mocking? Real input.
        return Prompt.strip_special_characters(input(prompt))

    # ======================================================================================================================
    # Private Support Functions.
    # ======================================================================================================================

    @staticmethod
    def set_mock_input(values: List[str]):
        # This will load the input to return a mock value.
        # Once used, the prompt will return to normal.
        Prompt.MOCK_INPUT_LOADED_VALUE = values

# ======================================================================================================================
# Also provide the methods as module level.
# ======================================================================================================================


def show_yes_no(text: str) -> bool:
    return Prompt.show_yes_no(text)


def show_text_input(text: str) -> str:
    return Prompt.show_text_input(text)


def show_options(text: str, options: List[PromptOption]):
    return Prompt.show_options(text, options)

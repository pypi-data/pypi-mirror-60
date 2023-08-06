from typing import List, Union
from .color import Color


class DictExpander:

    # Drawing the dictionaries.
    BOX_STEM = "├"
    BOX_STEM_END = "└"
    BOX_BRANCH = "─"
    BOX_BRANCH_DOWN = "┬"

    def __init__(self):
        pass

    @classmethod
    def recursive_expansion(
            cls, data: dict, output_list, stem_color: Union[str, None], value_color: Union[str, None],
            indent: int = 0, indent_end_stack: list = []):

        if data is not None:
            n_elements = 0
            for k, v in data.items():

                n_elements += 1
                use_key = str(k)
                is_last_element = not (n_elements < len(data))
                element_is_populated_dict = type(v) is dict and len(v) > 0

                stem_arr = []
                for i in range(indent):
                    stem_arr.append("│ " if not indent_end_stack[i] else "  ")

                stem_arr.append(cls.BOX_STEM_END if is_last_element else cls.BOX_STEM)
                stem_arr.append(cls.BOX_BRANCH)

                if element_is_populated_dict:
                    stem_arr.append(cls.BOX_BRANCH_DOWN)
                else:
                    stem_arr.append(cls.BOX_BRANCH)

                stem = "".join(stem_arr)

                if not element_is_populated_dict:
                    use_key += ":"  # Add a colon to the key before applying color.

                if stem_color is not None:
                    use_key = Color.set_color(stem_color, use_key)
                    stem = Color.set_color(stem_color, stem)

                if element_is_populated_dict:
                    line = f"  {stem} {use_key}"
                    output_list.append(line)
                    indent_end_stack.append(is_last_element)
                    cls.recursive_expansion(v, output_list, stem_color, value_color, indent + 1, indent_end_stack)
                    indent_end_stack.pop()
                else:

                    if type(v) == list:
                        # So lists appear without the quotes.
                        list_string = ", ".join([str(x) for x in v])
                        data_string = f"[{list_string}]"
                    else:
                        data_string = str(v)

                    if value_color is not None:
                        data_string = Color.set_color(value_color, data_string)
                    line = f"  {stem} {use_key} {data_string}"
                    output_list.append(line)

# ======================================================================================================================
# Expand the object.
# ======================================================================================================================


def expand(key: Union[str, None], data: dict,
           stem_color: Union[str, None] = None,
           value_color: Union[str, None] = None) -> List[str]:
    output = []
    if key is not None:
        # Convert key to string.
        key = str(key)

        # Color the key if needed.
        if stem_color is not None:
            key = Color.set_color(stem_color, key)

        # Add it to the display list and begin expansion.
        output.append(key)

    DictExpander.recursive_expansion(data, output, stem_color, value_color)
    return output

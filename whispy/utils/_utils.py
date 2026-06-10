import re

def format_markdown(text: str) -> str:
    """
    Format markdown strings to work as intended

    Forces correct markdown syntax as a convenience.

    1. ``'&nbsp;'`` is inserted between a sequence of two linebreaks ``'\n\n'``
       to force rendering of two line breaks (spaces between linebreaks
       allowed).
    2. Two blank spaces ``'  '`` are inserted before each line break to force
       the line break.

    Parameters
    ----------
    text : str
        markdown string

    Returns
    -------
    str
        markdown string with extended formatting
    """
    normalized = re.sub(r"\n[ ]*\n", "\n&nbsp;\n", text)
    return normalized.replace("\n", "  \n")
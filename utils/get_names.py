from typing import Literal

import names


def get_name(
    name_type: Literal["first", "last", "full"] = "first",
    gender: Literal["male", "female"] | None = None,
) -> str:
    """
    Get a random name using the names package.

    Args:
        name_type: Type of name to generate ('first', 'last', or 'full')
        gender: Gender for the name ('male', 'female', or None for any)

    Returns:
        Generated name string
    """
    if name_type == "first":
        return names.get_first_name(gender=gender)
    elif name_type == "last":
        return names.get_last_name()
    elif name_type == "full":
        first = names.get_first_name(gender=gender)
        last = names.get_last_name()
        return f"{first} {last}"
    else:
        raise ValueError(
            f"Invalid name_type: {name_type}. Must be 'first', 'last', or 'full'"
        )


def get_names(
    size: int,
    name_type: Literal["first", "last", "full"] = "first",
    gender: Literal["male", "female"] | None = None,
) -> list[str]:
    """
    Get a list of random names using the names package.

    Args:
        size: Number of names to generate
        name_type: Type of name to generate ('first', 'last', or 'full')
        gender: Gender for the names ('male', 'female', or None for any)

    Returns:
        List of generated name strings
    """
    return [get_name(name_type=name_type, gender=gender) for _ in range(size)]


def apply_case_formatting(
    name: str, case_format: Literal["title", "upper", "lower"] = "title"
) -> str:
    """
    Apply case formatting to a name string.

    Args:
        name: The name string to format
        case_format: The case format to apply ('title', 'upper', or 'lower')

    Returns:
        Formatted name string
    """
    if case_format == "title":
        return name  # names package already returns title case by default
    elif case_format == "upper":
        return name.upper()
    elif case_format == "lower":
        return name.lower()
    else:
        raise ValueError(
            f"Invalid case_format: {case_format}. Must be 'title', 'upper', or 'lower'"
        )

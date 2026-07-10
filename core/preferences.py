"""
Formats a raw extracted-constraints dict into a display-friendly
{label: value} mapping for the "Your Preferences" UI card — hides
default/empty sentinels, and turns Python types (bool, list) into
readable text instead of leaking their repr.
"""

_HIDDEN_VALUES = {"none", "null", "false", "", "[]", "{}", "unspecified"}
_HIDDEN_KEYS = {"raw"}


def format_preferences(constraints: dict) -> dict:
    if not isinstance(constraints, dict):
        return {}

    formatted = {}
    for key, value in constraints.items():
        if key in _HIDDEN_KEYS:
            continue

        if isinstance(value, bool):
            if not value:
                continue
            display_value = "Yes"

        elif isinstance(value, (list, tuple)):
            items = [str(v).strip() for v in value if str(v).strip()]
            if not items:
                continue
            display_value = ", ".join(item.title() for item in items)

        else:
            text = str(value).strip()
            if text.lower() in _HIDDEN_VALUES:
                continue
            display_value = text.title()

        label = key.replace("_", " ").title()
        formatted[label] = display_value

    return formatted

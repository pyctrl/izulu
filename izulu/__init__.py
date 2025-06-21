import logging
import typing as t


_IMPORT_ERROR_TEXT = (
    "",
    "You have early version of Python.",
    "  Extra compatibility dependency required.",
    "  Please add 'izulu[compatibility]' to your project dependencies.",
    "",
    "Pip: `pip install izulu[compatibility]`",
)

if not hasattr(t, "dataclass_transform"):
    try:
        import typing_extensions  # noqa
    except ImportError:
        for message in _IMPORT_ERROR_TEXT:
            logging.error(message)  # noqa: LOG015,TRY400
        raise

from __future__ import annotations

import typing as t


KWARGS = t.Dict[str, t.Any]

MAYBE_EXC = t.Optional[Exception]

EXC_CLS = t.Type[Exception]
EXC_MATCH = t.Union[EXC_CLS, t.Tuple[EXC_CLS, ...]]

USER_FN = t.Callable[[EXC_CLS, Exception, KWARGS], MAYBE_EXC]
ACTION = t.Union[EXC_CLS, USER_FN, None, t._SpecialForm]

RULE = t.Tuple[EXC_MATCH, ACTION]
RULES = t.Tuple[RULE, ...]

RERAISING = t.Union[bool, RULES]  # tup, chain?

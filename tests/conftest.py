import datetime

import pytest

from tests import errors


@pytest.fixture()
def derived_error():
    ts = datetime.datetime.now()
    return errors.DerivedError(name="John",
                               surname="Brown",
                               note="...",
                               age=42,
                               updated_at=ts,
                               full_name="secret",
                               box=dict())

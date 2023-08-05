import pytest
import logging


logger = logging.getLogger(__name__)


@pytest.mark.xfail
def test_blank():
    raise ZeroDivisionError()

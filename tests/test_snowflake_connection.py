import pytest
from dags.vantage_to_snowflake_v2 import return_snowflake_hook


def test_return_snowflake_hook():
    # Test connection and cursor retrieval
    cursor = return_snowflake_hook()
    assert cursor is not None
    assert hasattr(cursor, "execute")
    assert hasattr(cursor, "fetchone")

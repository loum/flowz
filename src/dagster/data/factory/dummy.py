"""Dummy data factory.

"""
from typing import Any, Optional
from pyspark.sql.types import Row

import dagster.schema.dummy


# pylint: disable=too-few-public-methods
class Data:
    """Dummy data."""

    def __init__(self, row_count: int = 2, skew: bool = False):
        self.row_count: int = row_count
        self.skew: bool = skew

    def rows(self) -> list[tuple[Optional[Any], ...]]:
        """Create a dynamic set of DataFrame rows.

        Row count based on `row_count`.

        """
        col = "dummy_col02_val"
        return [
            (i, f"{col}{i+1 if self.skew else i:0>10}")
            for i in range(1, self.row_count + 1)
        ]

    def args(self) -> tuple[Any, Any]:
        """Return a construct."""
        return (map(lambda x: Row(*x), self.rows()), dagster.schema.dummy.schema())

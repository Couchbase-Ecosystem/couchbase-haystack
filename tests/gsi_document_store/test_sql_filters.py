# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import datetime
import unittest
from typing import Dict, Any

import pandas as pd
import pytest
from haystack.errors import FilterError

from couchbase_haystack.document_stores.sql_filters import (
    normalize_sql_filters,
    _format_field_path,
    _format_value,
)


class TestSQLFilters:
    """Test suite for SQL++ filter normalization"""

    def test_normalize_filters_simple_comparison(self):
        """Test simple equality comparison"""
        filters = {"field": "name", "operator": "==", "value": "John Doe"}
        result = normalize_sql_filters(filters)
        assert result == "name = 'John Doe'"

    def test_normalize_filters_not_dict(self, invalid_filters):
        """Test error when filters is not a dictionary"""
        with pytest.raises(FilterError, match="Filters must be a dictionary"):
            normalize_sql_filters(invalid_filters["not_a_dict"])

    def test_format_field_path(self, field_path_filters):
        """Test field path formatting for SQL++"""
        # Simple fields
        assert _format_field_path("name") == "name"
        assert _format_field_path("document") == "document"

        # Nested fields
        assert _format_field_path("metadata.year") == "metadata.`year`"
        assert _format_field_path("doc.metadata.author.name") == "doc.`metadata`.`author`.`name`"

    def test_format_value(self):
        """Test value formatting for SQL++"""
        # Basic types
        assert _format_value(None) == "NULL"
        assert _format_value(True) == "true"
        assert _format_value(False) == "false"
        assert _format_value(123) == "123"
        assert _format_value(123.45) == "123.45"

        # Strings
        assert _format_value("hello") == "'hello'"
        assert _format_value("it's a quote") == "'it''s a quote'"  # Escaped quotes

        # ISO date
        date_str = "2023-01-01T12:00:00"
        assert _format_value(date_str) == f"'{date_str}'"

        # DataFrame
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        assert _format_value(df).startswith("'") and _format_value(df).endswith("'")

    def test_comparison_operators(self, comparison_filters):
        """Test all comparison operators"""
        # Equality
        assert normalize_sql_filters(comparison_filters["equality"]) == "name = 'John Doe'"

        # Inequality
        assert normalize_sql_filters(comparison_filters["inequality"]) == "(status != 'done' OR status IS MISSING)"

        # Greater than
        assert normalize_sql_filters(comparison_filters["greater_than"]) == "score > 80"

        # Greater than or equal
        assert normalize_sql_filters(comparison_filters["greater_than_equal"]) == "score >= 80"

        # Less than
        assert normalize_sql_filters(comparison_filters["less_than"]) == "score < 80"

        # Less than or equal
        assert normalize_sql_filters(comparison_filters["less_than_equal"]) == "score <= 80"

        # In operator
        assert normalize_sql_filters(comparison_filters["in_operator"]) == "status IN ['open', 'pending']"

        # Not in operator
        assert (
            normalize_sql_filters(comparison_filters["not_in_operator"])
            == "(status NOT IN ['closed', 'rejected'] OR status IS MISSING)"
        )

        # NULL values
        assert normalize_sql_filters(comparison_filters["null_equality"]) == "(description IS NULL OR description IS MISSING)"
        assert (
            normalize_sql_filters(comparison_filters["null_inequality"])
            == "(description IS NOT NULL AND description IS NOT MISSING)"
        )

    def test_logical_operators(self, logical_filters):
        """Test all logical operators"""
        # AND operator
        assert normalize_sql_filters(logical_filters["and_filter"]) == "(age > 18 AND status = 'active')"

        # OR operator
        assert normalize_sql_filters(logical_filters["or_filter"]) == "(category = 'books' OR category = 'magazines')"

        # Empty conditions
        assert normalize_sql_filters(logical_filters["empty_conditions"]) == "TRUE"

    def test_nested_conditions(self, nested_filters):
        """Test nested logical conditions"""
        assert normalize_sql_filters(nested_filters["and_with_or"]) == "(age >= 18 AND (role = 'admin' OR role = 'moderator'))"
        assert (
            normalize_sql_filters(nested_filters["or_with_and"])
            == "((category = 'books' AND price < 20) OR (category = 'electronics' AND discount > 0.2))"
        )

        # Test deeply nested filter
        expected = "(featured = true OR (price < 100 AND (category = 'clothing' OR sale = true)))"
        assert normalize_sql_filters(nested_filters["deeply_nested"]) == expected

    def test_edge_cases(self):
        """Test edge cases and special values"""
        # Value is a list for equality
        filters = {"field": "tags", "operator": "==", "value": ["red", "blue"]}
        expected = "(tags = 'red' AND tags = 'blue')"
        assert normalize_sql_filters(filters) == expected

        # Value is a list for inequality
        filters = {"field": "tags", "operator": "!=", "value": ["red", "blue"]}
        expected = "((tags != 'red' OR tags IS MISSING) AND (tags != 'blue' OR tags IS MISSING))"
        assert normalize_sql_filters(filters) == expected

    def test_error_cases(self, invalid_filters):
        """Test error conditions"""
        # Missing 'operator' key in comparison
        with pytest.raises(FilterError, match="'operator' key missing"):
            normalize_sql_filters(invalid_filters["missing_operator_comparison"])

        # Missing 'value' key in comparison
        with pytest.raises(FilterError, match="'value' key missing"):
            normalize_sql_filters(invalid_filters["missing_value_comparison"])

        # Missing 'operator' key in logical condition
        with pytest.raises(FilterError, match="'operator' key missing"):
            normalize_sql_filters(invalid_filters["missing_operator_logical"])

        # Missing 'conditions' key in logical condition
        with pytest.raises(FilterError, match="'conditions' key missing"):
            normalize_sql_filters(invalid_filters["missing_conditions"])

        # Unknown logical operator
        with pytest.raises(FilterError, match="Unknown logical operator"):
            normalize_sql_filters(invalid_filters["unknown_logical_operator"])

        # Comparison with invalid type
        with pytest.raises(FilterError, match="Filter value can't be of type"):
            normalize_sql_filters(invalid_filters["invalid_type_comparison"])

        # String comparison with non-date
        with pytest.raises(FilterError, match="Strings are only comparable if they are ISO formatted dates"):
            normalize_sql_filters(invalid_filters["string_comparison"])

        # 'in' operator with non-list value
        with pytest.raises(FilterError, match="must be a list when using 'in' or 'not in'"):
            normalize_sql_filters(invalid_filters["in_with_non_list"])

    def test_date_comparisons(self, date_filters):
        """Test date string comparisons"""
        date_str = "2023-01-01T12:00:00"

        # Test each date comparison type
        assert normalize_sql_filters(date_filters["greater_than"]) == f"created_at > '{date_str}'"
        assert normalize_sql_filters(date_filters["greater_than_equal"]) == f"created_at >= '{date_str}'"
        assert normalize_sql_filters(date_filters["less_than"]) == f"created_at < '{date_str}'"
        assert normalize_sql_filters(date_filters["less_than_equal"]) == f"created_at <= '{date_str}'"
        assert normalize_sql_filters(date_filters["equality"]) == f"created_at = '{date_str}'"
        assert normalize_sql_filters(date_filters["inequality"]) == f"(created_at != '{date_str}' OR created_at IS MISSING)"

    def test_complex_nested_field_paths(self, field_path_filters):
        """Test complex nested field paths"""
        # Test dot notation handling
        assert normalize_sql_filters(field_path_filters["dot_notation"]) == "metadata.`year` = 2023"

        # Test deeply nested paths
        expected = "user.`profile`.`contact`.`email` = 'user@example.com'"
        assert normalize_sql_filters(field_path_filters["nested_field"]) == expected

        # Test nested logical condition with field paths
        expected = "(metadata.`author`.`name` = 'John Doe' AND metadata.`published`.`year` > 2020)"
        assert normalize_sql_filters(field_path_filters["nested_logical"]) == expected

    def test_real_world_scenarios(self):
        """Test real-world filter scenarios"""
        # Complex filter combining multiple conditions and types
        filters = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.year", "operator": ">=", "value": 2020},
                {"field": "metadata.author", "operator": "==", "value": "Jane Doe"},
                {
                    "operator": "OR",
                    "conditions": [
                        {"field": "category", "operator": "in", "value": ["fiction", "biography"]},
                        {"field": "rating", "operator": ">=", "value": 4.5},
                    ],
                },
            ],
        }

        # Get the actual SQL filter
        actual = normalize_sql_filters(filters)

        # Expected SQL filter (with formatting for readability)
        expected = (
            "(metadata.`year` >= 2020 AND "
            "metadata.`author` = 'Jane Doe' AND "
            "(category IN ['fiction', 'biography'] OR rating >= 4.5))"
        )

        # Compare by normalizing whitespace in both strings
        def normalize_whitespace(s):
            return ' '.join(s.split())

        assert normalize_whitespace(actual) == normalize_whitespace(expected)


if __name__ == "__main__":
    unittest.main()

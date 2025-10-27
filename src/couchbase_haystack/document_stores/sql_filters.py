# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Any, Dict

from haystack.errors import FilterError
from pandas import DataFrame


def normalize_sql_filters(filters: Dict[str, Any]) -> str:
    """
    Converts Haystack filters to a SQL++ (N1QL) compatible WHERE clause.

    :param filters: The Haystack filters dictionary
    :returns: SQL++ compatible WHERE clause string
    :raises FilterError: If the filters are invalid
    """
    if not isinstance(filters, dict):
        msg = "Filters must be a dictionary"
        raise FilterError(msg)

    if "field" in filters:
        return _parse_comparison_condition(filters)
    return _parse_logical_condition(filters)


def _parse_logical_condition(condition: Dict[str, Any]) -> str:
    """
    Parses a logical condition (AND, OR, NOT) into a SQL++ compatible string.

    :param condition: The logical condition dictionary
    :returns: SQL++ compatible logical condition string
    :raises FilterError: If the condition is invalid
    """
    if "operator" not in condition:
        msg = f"'operator' key missing in {condition}"
        raise FilterError(msg)
    if "conditions" not in condition:
        msg = f"'conditions' key missing in {condition}"
        raise FilterError(msg)

    operator = condition["operator"]
    conditions = [_parse_comparison_condition(c) for c in condition["conditions"]]

    if len(conditions) == 0:
        return "TRUE"  # Default to true for empty conditions

    if operator == "AND":
        return f"({' AND '.join(conditions)})"
    elif operator == "OR":
        return f"({' OR '.join(conditions)})"
    elif operator == "NOT":
        msg = "NOT operator is not supported. Only AND and OR logical operators are supported."
        raise FilterError(msg)
    else:
        msg = f"Unknown logical operator '{operator}'"
        raise FilterError(msg)


def _parse_comparison_condition(condition: Dict[str, Any]) -> str:
    """
    Parses a comparison condition (==, !=, >, >=, <, <=, in, not in) into a SQL++ compatible string.

    :param condition: The comparison condition dictionary
    :returns: SQL++ compatible comparison condition string
    :raises FilterError: If the condition is invalid
    """
    if "field" not in condition:
        # 'field' key is only found in comparison dictionaries.
        # We assume this is a logic dictionary since it's not present.
        return _parse_logical_condition(condition)

    field: str = condition["field"]

    if "operator" not in condition:
        msg = f"'operator' key missing in {condition}"
        raise FilterError(msg)
    if "value" not in condition:
        msg = f"'value' key missing in {condition}"
        raise FilterError(msg)

    operator: str = condition["operator"]
    value: Any = condition["value"]

    # Format the field path correctly for SQL++ nested field access
    formatted_field = _format_field_path(field)

    return COMPARISON_OPERATORS[operator](formatted_field, value)


def _format_field_path(field: str) -> str:
    """
    Formats a field path for SQL++ nested field access.

    Handles dot notation and converts it to proper SQL++ syntax.
    Example: "metadata.year" becomes "metadata.`year`"

    :param field: The field path
    :returns: SQL++ compatible field path
    """
    parts = field.split(".")

    # Keep the first part as is (it's usually the document or alias)
    if len(parts) <= 1:
        return field

    # Format remaining parts with backticks to handle reserved keywords and special characters
    formatted_parts = [parts[0]] + [f"`{part}`" for part in parts[1:]]
    return ".".join(formatted_parts)


def _equal(field: str, value: Any) -> str:
    """
    Generates SQL++ equality comparison

    :param field: Field name
    :param value: Value to compare
    :returns: SQL++ equality condition
    """
    if value is None:
        return f"({field} IS NULL OR {field} IS MISSING)"
    if isinstance(value, list):
        # Handle list of values (generate multiple equality conditions)
        conditions = [f"{field} = {_format_value(v)}" for v in value]
        return f"({' AND '.join(conditions)})"
    return f"{field} = {_format_value(value)}"


def _not_equal(field: str, value: Any) -> str:
    """
    Generates SQL++ not equal comparison

    :param field: Field name
    :param value: Value to compare
    :returns: SQL++ not equal condition
    """
    if value is None:
        return f"({field} IS NOT NULL AND {field} IS NOT MISSING)"
    if isinstance(value, list):
        # Handle list of values (generate multiple inequality conditions)
        conditions = [_not_equal(field, v) for v in value]
        return f"({' AND '.join(conditions)})"
    return f"({field} != {_format_value(value)} OR {field} IS MISSING)"


def _greater_than(field: str, value: Any) -> str:
    """
    Generates SQL++ greater than comparison

    :param field: Field name
    :param value: Value to compare
    :returns: SQL++ greater than condition
    :raises FilterError: If the value type is incompatible
    """
    if value is None:
        # When value is None, match no documents (impossible condition)
        return "FALSE"
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return f"{field} > '{value}'"
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if isinstance(value, (list, DataFrame)):
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return f"{field} > {_format_value(value)}"


def _greater_than_equal(field: str, value: Any) -> str:
    """
    Generates SQL++ greater than or equal comparison

    :param field: Field name
    :param value: Value to compare
    :returns: SQL++ greater than or equal condition
    :raises FilterError: If the value type is incompatible
    """
    if value is None:
        # When value is None, match no documents (impossible condition)
        return "FALSE"
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return f"{field} >= '{value}'"
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if isinstance(value, (list, DataFrame)):
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return f"{field} >= {_format_value(value)}"


def _less_than(field: str, value: Any) -> str:
    """
    Generates SQL++ less than comparison

    :param field: Field name
    :param value: Value to compare
    :returns: SQL++ less than condition
    :raises FilterError: If the value type is incompatible
    """
    if value is None:
        # When value is None, match no documents (impossible condition)
        return "FALSE"
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return f"{field} < '{value}'"
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if isinstance(value, (list, DataFrame)):
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return f"{field} < {_format_value(value)}"


def _less_than_equal(field: str, value: Any) -> str:
    """
    Generates SQL++ less than or equal comparison

    :param field: Field name
    :param value: Value to compare
    :returns: SQL++ less than or equal condition
    :raises FilterError: If the value type is incompatible
    """
    if value is None:
        # When value is None, match no documents (impossible condition)
        return "FALSE"
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return f"{field} <= '{value}'"
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if isinstance(value, (list, DataFrame)):
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return f"{field} <= {_format_value(value)}"


def _in(field: str, value: Any) -> str:
    """
    Generates SQL++ IN comparison

    :param field: Field name
    :param value: List of values to check against
    :returns: SQL++ IN condition
    :raises FilterError: If the value is not a list
    """
    if not isinstance(value, list):
        msg = f"{field}'s value must be a list when using 'in' or 'not in' comparators"
        raise FilterError(msg)
    if not value:
        # Empty list means no matches (impossible condition)
        return "FALSE"
    formatted_values = [_format_value(v) for v in value]
    values_str = ", ".join(formatted_values)
    return f"{field} IN [{values_str}]"


def _not_in(field: str, value: Any) -> str:
    """
    Generates SQL++ NOT IN comparison

    :param field: Field name
    :param value: List of values to check against
    :returns: SQL++ NOT IN condition
    :raises FilterError: If the value is not a list
    """
    if not isinstance(value, list):
        msg = f"{field}'s value must be a list when using 'in' or 'not in' comparators"
        raise FilterError(msg)
    if not value:
        # Empty list means match all (always true)
        return "TRUE"

    formatted_values = [_format_value(v) for v in value if v]
    values_str = ", ".join(formatted_values)
    # Check if None is in the list
    if None in value:
        # If None is in the list, don't match NULL or MISSING fields
        return f"{field} NOT IN [{values_str}]"
    else:
        # If None is not in the list, also match NULL or MISSING fields
        return f"({field} NOT IN [{values_str}] OR {field} IS MISSING)"


def _format_value(value: Any) -> str:
    """
    Formats a value for use in a SQL++ query.

    :param value: The value to format
    :returns: SQL++ compatible value string
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Check if it's a date string
        try:
            datetime.fromisoformat(value)
            return f"'{value}'"
        except (ValueError, TypeError):
            # Escape single quotes in strings
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
    if isinstance(value, DataFrame):
        # Convert DataFrame to JSON string
        json_str = value.to_json()
        escaped_json = json_str.replace("'", "''")
        return f"'{escaped_json}'"
    # Fallback to string representation with quotes
    str_value = str(value)
    escaped_str = str_value.replace("'", "''")
    return f"'{escaped_str}'"


# Map of Haystack filter operators to SQL++ filter functions
COMPARISON_OPERATORS = {
    "==": _equal,
    "!=": _not_equal,
    ">": _greater_than,
    ">=": _greater_than_equal,
    "<": _less_than,
    "<=": _less_than_equal,
    "in": _in,
    "not in": _not_in,
}

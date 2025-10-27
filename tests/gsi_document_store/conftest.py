# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import pytest
from typing import Dict, Any, List


@pytest.fixture
def comparison_filters() -> Dict[str, Dict[str, Any]]:
    """
    Fixture providing sample comparison filters for testing
    """
    return {
        "equality": {"field": "name", "operator": "==", "value": "John Doe"},
        "inequality": {"field": "status", "operator": "!=", "value": "done"},
        "greater_than": {"field": "score", "operator": ">", "value": 80},
        "greater_than_equal": {"field": "score", "operator": ">=", "value": 80},
        "less_than": {"field": "score", "operator": "<", "value": 80},
        "less_than_equal": {"field": "score", "operator": "<=", "value": 80},
        "in_operator": {"field": "status", "operator": "in", "value": ["open", "pending"]},
        "not_in_operator": {"field": "status", "operator": "not in", "value": ["closed", "rejected"]},
        "null_equality": {"field": "description", "operator": "==", "value": None},
        "null_inequality": {"field": "description", "operator": "!=", "value": None},
    }


@pytest.fixture
def logical_filters() -> Dict[str, Dict[str, Any]]:
    """
    Fixture providing sample logical filters for testing
    """
    return {
        "and_filter": {
            "operator": "AND",
            "conditions": [
                {"field": "age", "operator": ">", "value": 18},
                {"field": "status", "operator": "==", "value": "active"},
            ],
        },
        "or_filter": {
            "operator": "OR",
            "conditions": [
                {"field": "category", "operator": "==", "value": "books"},
                {"field": "category", "operator": "==", "value": "magazines"},
            ],
        },
        "empty_conditions": {"operator": "AND", "conditions": []},
    }


@pytest.fixture
def nested_filters() -> Dict[str, Dict[str, Any]]:
    """
    Fixture providing sample nested filters for testing
    """
    return {
        "and_with_or": {
            "operator": "AND",
            "conditions": [
                {"field": "age", "operator": ">=", "value": 18},
                {
                    "operator": "OR",
                    "conditions": [
                        {"field": "role", "operator": "==", "value": "admin"},
                        {"field": "role", "operator": "==", "value": "moderator"},
                    ],
                },
            ],
        },
        "or_with_and": {
            "operator": "OR",
            "conditions": [
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "category", "operator": "==", "value": "books"},
                        {"field": "price", "operator": "<", "value": 20},
                    ],
                },
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "category", "operator": "==", "value": "electronics"},
                        {"field": "discount", "operator": ">", "value": 0.2},
                    ],
                },
            ],
        },
        "deeply_nested": {
            "operator": "OR",
            "conditions": [
                {"field": "featured", "operator": "==", "value": True},
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "price", "operator": "<", "value": 100},
                        {
                            "operator": "OR",
                            "conditions": [
                                {"field": "category", "operator": "==", "value": "clothing"},
                                {"field": "sale", "operator": "==", "value": True},
                            ],
                        },
                    ],
                },
            ],
        },
    }


@pytest.fixture
def invalid_filters() -> Dict[str, Any]:
    """
    Fixture providing invalid filters that should raise exceptions
    """
    return {
        "not_a_dict": "invalid_filter",
        "missing_operator_comparison": {"field": "name", "value": "John"},
        "missing_value_comparison": {"field": "name", "operator": "=="},
        "missing_operator_logical": {"conditions": [{"field": "name", "operator": "==", "value": "John"}]},
        "missing_conditions": {"operator": "AND"},
        "unknown_logical_operator": {"operator": "XOR", "conditions": [{"field": "age", "operator": ">", "value": 18}]},
        "invalid_type_comparison": {"field": "age", "operator": ">", "value": [1, 2, 3]},
        "string_comparison": {"field": "name", "operator": ">", "value": "John"},
        "in_with_non_list": {"field": "status", "operator": "in", "value": "active"},
    }


@pytest.fixture
def date_filters() -> Dict[str, Dict[str, Any]]:
    """
    Fixture providing filters with date comparisons
    """
    date_str = "2023-01-01T12:00:00"
    return {
        "greater_than": {"field": "created_at", "operator": ">", "value": date_str},
        "greater_than_equal": {"field": "created_at", "operator": ">=", "value": date_str},
        "less_than": {"field": "created_at", "operator": "<", "value": date_str},
        "less_than_equal": {"field": "created_at", "operator": "<=", "value": date_str},
        "equality": {"field": "created_at", "operator": "==", "value": date_str},
        "inequality": {"field": "created_at", "operator": "!=", "value": date_str},
    }


@pytest.fixture
def field_path_filters() -> Dict[str, Dict[str, Any]]:
    """
    Fixture providing filters with complex field paths
    """
    return {
        "simple_field": {"field": "name", "operator": "==", "value": "John Doe"},
        "dot_notation": {"field": "metadata.year", "operator": "==", "value": 2023},
        "nested_field": {"field": "user.profile.contact.email", "operator": "==", "value": "user@example.com"},
        "nested_logical": {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.author.name", "operator": "==", "value": "John Doe"},
                {"field": "metadata.published.year", "operator": ">", "value": 2020},
            ],
        },
    }

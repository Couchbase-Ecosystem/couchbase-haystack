# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Any, Dict, List, Optional

from couchbase import search
from couchbase.logic.search_queries import SearchQuery
from haystack.errors import FilterError
from pandas import DataFrame
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()

class DateRangeQuery(search.DateRangeQuery):
    @property
    def inclusive_start(self) -> Optional[bool]:
        return self._json_.get("inclusive_start", None)

    @inclusive_start.setter
    def inclusive_start(
        self, value  # type: bool
    ) -> None:
        self.set_prop("inclusive_start", value)

    @property
    def inclusive_end(self) -> Optional[bool]:
        return self._json_.get("inclusive_end", None)

    @inclusive_end.setter
    def inclusive_end(
        self, value  # type: bool
    ) -> None:
        self.set_prop("inclusive_end", value)


class NumericRangeQuery(search.NumericRangeQuery):
    @property
    def inclusive_min(self) -> Optional[bool]:
        return self._json_.get("inclusive_min", None)

    @inclusive_min.setter
    def inclusive_min(
        self, value  # type: bool
    ) -> None:
        self.set_prop("inclusive_min", value)

    @property
    def inclusive_max(self) -> Optional[bool]:
        return self._json_.get("inclusive_max", None)

    @inclusive_max.setter
    def inclusive_max(
        self, value  # type: bool
    ) -> None:
        self.set_prop("inclusive_max", value)


def _normalize_filters(filters: Dict[str, Any]) -> SearchQuery:
    """
    Converts Haystack filters in Couchbase compatible filters.
    """
    if not isinstance(filters, dict):
        msg = "Filters must be a dictionary"
        raise FilterError(msg)

    if "field" in filters:
        return _parse_comparison_condition(filters)
    return _parse_logical_condition(filters)


def _parse_logical_condition(condition: Dict[str, Any]) -> SearchQuery:
    if "operator" not in condition:
        msg = f"'operator' key missing in {condition}"
        raise FilterError(msg)
    if "conditions" not in condition:
        msg = f"'conditions' key missing in {condition}"
        raise FilterError(msg)

    operator = condition["operator"]
    conditions = [_parse_comparison_condition(c) for c in condition["conditions"]]
    # if len(conditions) > 1:
    #     conditions = _normalize_ranges(conditions)
    if operator == "AND":
        return search.BooleanQuery(must=search.ConjunctionQuery(*conditions))
    elif operator == "OR":
        return search.BooleanQuery(should=search.DisjunctionQuery(*conditions))
    elif operator == "NOT":
        return search.BooleanQuery(must_not=search.DisjunctionQuery(*conditions, min=len(conditions)))
    else:
        msg = f"Unknown logical operator '{operator}'"
        raise FilterError(msg)


def _equal(field: str, value: Any) -> Dict[str, Any]:
    if value is None:
        raise Exception("None value filter not supported")
    if isinstance(value, list):
        conjunction = [create_search_query(field=field, value=v) for v in value]
        return search.BooleanQuery(must=search.ConjunctionQuery(*conjunction))
    if field == "dataframe" and isinstance(value, DataFrame):
        value = value.to_json()
    return create_search_query(field=field, value=value)


def _not_equal(field: str, value: Any) -> Dict[str, Any]:
    if value is None:
        raise Exception("None value filter not supported")

    if isinstance(value, list):
        conjunction = [create_search_query(field=field, value=v) for v in value]
        return search.BooleanQuery(must_not=search.DisjunctionQuery(*conjunction, min=len(conjunction)))
    if field == "dataframe" and isinstance(value, DataFrame):
        value = value.to_json()
    return search.BooleanQuery(must_not=search.DisjunctionQuery(create_search_query(field=field, value=value)))


def _greater_than(field: str, value: Any) -> Dict[str, Any]:
    if value is None:
        # When the value is None and '>' is used we create a filter that would return a Document
        # if it has a field set and not set at the same time.
        # This will cause the filter to match no Document.
        # This way we keep the behavior consistent with other Document Stores.
        raise Exception("None value filter not supported")
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return search.DateRangeQuery(start=value, field=field)
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if type(value) in [list, DataFrame]:
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return NumericRangeQuery(min=value, field=field)


def _greater_than_equal(field: str, value: Any) -> Dict[str, Any]:
    if value is None:
        # When the value is None and '>=' is used we create a filter that would return a Document
        # if it has a field set and not set at the same time.
        # This will cause the filter to match no Document.
        # This way we keep the behavior consistent with other Document Stores.
        raise Exception("None value filter not supported")
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            filter = DateRangeQuery(start=value, field=field)
            filter.inclusive_start = True
            return filter
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if type(value) in [list, DataFrame]:
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return NumericRangeQuery(min=value, field=field, inclusive_min=True)


def _less_than(field: str, value: Any) -> Dict[str, Any]:
    if value is None:
        # When the value is None and '<' is used we create a filter that would return a Document
        # if it has a field set and not set at the same time.
        # This will cause the filter to match no Document.
        # This way we keep the behavior consistent with other Document Stores.
        raise Exception("None value filter not supported")
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return search.DateRangeQuery(end=value, field=field)
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if type(value) in [list, DataFrame]:
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return NumericRangeQuery(max=value, field=field)


def _less_than_equal(field: str, value: Any) -> Dict[str, Any]:
    if value is None:
        # When the value is None and '<=' is used we create a filter that would return a Document
        # if it has a field set and not set at the same time.
        # This will cause the filter to match no Document.
        # This way we keep the behavior consistent with other Document Stores.
        raise Exception("None value filter not supported")
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            filter = DateRangeQuery(end=value, field=field)
            filter.inclusive_end = True
            return filter
        except (ValueError, TypeError) as exc:
            msg = (
                "Can't compare strings using operators '>', '>=', '<', '<='. "
                "Strings are only comparable if they are ISO formatted dates."
            )
            raise FilterError(msg) from exc
    if type(value) in [list, DataFrame]:
        msg = f"Filter value can't be of type {type(value)} using operators '>', '>=', '<', '<='"
        raise FilterError(msg)
    return NumericRangeQuery(max=value, field=field, inclusive_max=True)


def _in(field: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, list):
        msg = f"{field}'s value must be a list when using 'in' or 'not in' comparators"
        raise FilterError(msg)
    return search.BooleanQuery(should=search.DisjunctionQuery(*[create_search_query(field=field, value=v) for v in value]))


def _not_in(field: str, value: List[Any]) -> Dict[str, Any]:
    if not isinstance(value, list):
        msg = f"{field}'s value must be a list when using 'in' or 'not in' comparators"
        raise FilterError(msg)
    return search.BooleanQuery(
        must_not=search.DisjunctionQuery(*[create_search_query(field=field, value=v) for v in value], min=len(value))
    )


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


def create_search_query(field: str, value: Any) -> SearchQuery:
    if isinstance(value, (int, float)):
        number_filter = NumericRangeQuery(min=value, max=value, field=field, inclusive_min=True, inclusive_max=True)
        return number_filter
    try:
        datetime.fromisoformat(value)
        return DateRangeQuery(start=value, end=value, field=field, inclusive_start=True, inclusive_end=True)
    except (ValueError, TypeError):
        pass
    return search.MatchQuery(value, field=field)


def _parse_comparison_condition(condition: Dict[str, Any]) -> Dict[str, Any]:
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
    if isinstance(value, DataFrame):
        value = value.to_json()

    return COMPARISON_OPERATORS[operator](field, value)


def _normalize_ranges(conditions: List[search.SearchQuery]) -> List[search.SearchQuery]:
    """
    Merges range conditions acting on the same field.

    Args:
        conditions (List[search.SearchQuery]): List of search conditions.

    Returns:
        List[search.SearchQuery]: List with merged range conditions.
    """
    # Extract range conditions and associated field names
    range_conditions = [
        (query.field, query) for query in conditions if isinstance(query, NumericRangeQuery) or isinstance(query, DateRangeQuery)
    ]

    if range_conditions:
        # Remove range conditions from the original list
        conditions = [c for c in conditions if not isinstance(c, NumericRangeQuery) and not isinstance(c, DateRangeQuery)]

        # Dictionary to hold merged range conditions
        range_conditions_dict: Dict[str, Dict[str, Any]] = {}

        for field_name, query in range_conditions:
            encodable = query.encodable
            if field_name not in range_conditions_dict:
                range_conditions_dict[field_name] = {}
            for key, value in encodable.items():
                if key not in range_conditions_dict[field_name]:
                    range_conditions_dict[field_name][key] = value
                else:
                    range_conditions_dict[field_name].update({key: value})

        for _field_name, comparisons in range_conditions_dict.items():
            if "start" in comparisons or "end" in comparisons:
                conditions.append(DateRangeQuery(**comparisons))
            else:
                conditions.append(NumericRangeQuery(**comparisons))

    return conditions

---
id: document_filter
title: DocumentFilter
---

# Couchbase Filter and Query Utilities

This module provides utilities for handling and normalizing filters and queries for use with Couchbase's search capabilities, specifically tailored for integration with the Haystack framework. The utilities include custom classes and functions to handle date range and numeric range queries, as well as functions to normalize filters into Couchbase-compatible search queries.

## Class Overview

### `DateRangeQuery`

The `DateRangeQuery` class extends Couchbase's `DateRangeQuery` to provide additional properties for inclusive start and end dates.

#### Properties

- `inclusive_start` (Optional[bool]): Indicates whether the start of the date range is inclusive.
- `inclusive_end` (Optional[bool]): Indicates whether the end of the date range is inclusive.

**Example Usage:**

```python
date_query = DateRangeQuery(start="2024-01-01T00:00:00Z", end="2024-12-31T23:59:59Z", field="created_at")
date_query.inclusive_start = True
date_query.inclusive_end = True
```

### `NumericRangeQuery`

The `NumericRangeQuery` class extends Couchbase's `NumericRangeQuery` to provide additional properties for inclusive minimum and maximum values.

#### Properties

- `inclusive_min` (Optional[bool]): Indicates whether the minimum value is inclusive.
- `inclusive_max` (Optional[bool]): Indicates whether the maximum value is inclusive.

**Example Usage:**

```python
numeric_query = NumericRangeQuery(min=10, max=100, field="price")
numeric_query.inclusive_min = True
numeric_query.inclusive_max = True
```

## Function Overview

### `_normalize_filters`

```python
def _normalize_filters(filters: Dict[str, Any]) -> SearchQuery
```

**Description:**
- Converts Haystack-style filters into Couchbase-compatible search queries.

**Input Parameters:**
- `filters` (Dict[str, Any]): A dictionary representing the filters to be normalized.

**Response:**
- Returns a `SearchQuery` object that can be used in Couchbase search operations.

**Raises:**
- `FilterError`: If the filters provided are not in the expected format.

**Example Usage:**

```python
filters = {
    "operator": "AND",
    "conditions": [
        {"field": "price", "operator": ">=", "value": 10},
        {"field": "created_at", "operator": "<=", "value": "2024-12-31T23:59:59Z"}
    ]
}
search_query = _normalize_filters(filters)
```

### `_parse_logical_condition`

```python
def _parse_logical_condition(condition: Dict[str, Any]) -> SearchQuery
```

**Description:**
- Parses a logical condition (AND, OR, NOT) into a Couchbase `SearchQuery`.

**Input Parameters:**
- `condition` (Dict[str, Any]): A dictionary representing the logical condition.

**Response:**
- Returns a `SearchQuery` object that represents the logical condition.

**Example Usage:**

```python
logical_condition = {
    "operator": "AND",
    "conditions": [
        {"field": "status", "operator": "==", "value": "active"},
        {"field": "price", "operator": "<", "value": 50}
    ]
}
search_query = _parse_logical_condition(logical_condition)
```

### `_parse_comparison_condition`

```python
def _parse_comparison_condition(condition: Dict[str, Any]) -> Dict[str, Any]
```

**Description:**
- Parses a comparison condition (e.g., `==`, `>`, `<=`) into a Couchbase `SearchQuery`.

**Input Parameters:**
- `condition` (Dict[str, Any]): A dictionary representing the comparison condition.

**Response:**
- Returns a `SearchQuery` object that represents the comparison condition.

**Raises:**
- `FilterError`: If the condition is not properly formatted or contains unsupported types.

**Example Usage:**

```python
comparison_condition = {
    "field": "created_at",
    "operator": ">=",
    "value": "2024-01-01T00:00:00Z"
}
search_query = _parse_comparison_condition(comparison_condition)
```

### `create_search_query`

```python
def create_search_query(field: str, value: Any) -> SearchQuery
```

**Description:**
- Creates a Couchbase `SearchQuery` based on the field and value provided.

**Input Parameters:**
- `field` (str): The name of the field to query.
- `value` (Any): The value to query for. Can be a number, date, or string.

**Response:**
- Returns a `SearchQuery` object that matches the field and value provided.

**Example Usage:**

```python
search_query = create_search_query("price", 25)
```
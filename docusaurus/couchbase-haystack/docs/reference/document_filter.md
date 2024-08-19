---
id: document_filter
title: DocumentFilter
---

## Classes

### DateRangeQuery

This class extends the `DateRangeQuery` from Couchbase to add support for inclusive start and end properties.

```python
from datetime import datetime
from typing import Optional

class DateRangeQuery(search.DateRangeQuery):
    @property
    def inclusive_start(self) -> Optional[bool]:
        return self._json_.get('inclusive_start', None)

    @inclusive_start.setter
    def inclusive_start(self, value: bool) -> None:
        self.set_prop('inclusive_start', value)

    @property
    def inclusive_end(self) -> Optional[bool]:
        return self._json_.get('inclusive_end', None)

    @inclusive_end.setter
    def inclusive_end(self, value: bool) -> None:
        self.set_prop('inclusive_end', value)
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L10)

### NumericRangeQuery

This class extends the `NumericRangeQuery` from Couchbase to add support for inclusive min and max properties.

```python
class NumericRangeQuery(search.NumericRangeQuery):
    @property
    def inclusive_min(self) -> Optional[bool]:
        return self._json_.get('inclusive_min', None)

    @inclusive_min.setter
    def inclusive_min(self, value: bool) -> None:
        self.set_prop('inclusive_min', value)

    @property
    def inclusive_max(self) -> Optional[bool]:
        return self._json_.get('inclusive_max', None)

    @inclusive_max.setter
    def inclusive_max(self, value: bool) -> None:
        self.set_prop('inclusive_max', value)
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L26)

## Functions

### `_normalize_filters`

Converts Haystack filters into Couchbase-compatible filters.

- **Input**: 
  - `filters` (Dict[str, Any]): A dictionary of filters to normalize.
- **Output**: 
  - `SearchQuery`: A Couchbase-compatible search query object.

```python
def _normalize_filters(filters: Dict[str, Any]) -> SearchQuery:
    """
    Converts Haystack filters in Couchbase compatible filters.
    """
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L40)

### `_parse_logical_condition`

Parses logical conditions (AND, OR, NOT) in filters.

- **Input**: 
  - `condition` (Dict[str, Any]): A dictionary representing the logical condition to parse.
- **Output**: 
  - `SearchQuery`: A Couchbase-compatible search query object representing the logical condition.

```python
def _parse_logical_condition(condition: Dict[str, Any]) -> SearchQuery:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L51)

### `_equal`

Handles equality conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the equality condition on.
  - `value` (Any): The value to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the equality condition.

```python
def _equal(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L71)

### `_not_equal`

Handles inequality conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the inequality condition on.
  - `value` (Any): The value to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the inequality condition.

```python
def _not_equal(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L84)

### `_greater_than`

Handles "greater than" conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the "greater than" condition on.
  - `value` (Any): The value to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the "greater than" condition.

```python
def _greater_than(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L98)

### `_greater_than_equal`

Handles "greater than or equal to" conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the "greater than or equal to" condition on.
  - `value` (Any): The value to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the "greater than or equal to" condition.

```python
def _greater_than_equal(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L117)

### `_less_than`

Handles "less than" conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the "less than" condition on.
  - `value` (Any): The value to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the "less than" condition.

```python
def _less_than(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L139)

### `_less_than_equal`

Handles "less than or equal to" conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the "less than or equal to" condition on.
  - `value` (Any): The value to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the "less than or equal to" condition.

```python
def _less_than_equal(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L156)

### `_in`

Handles "in" conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the "in" condition on.
  - `value` (Any): The list of values to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the "in" condition.

```python
def _in(field: str, value: Any) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L179)

### `_not_in`

Handles "not in" conditions in filters.

- **Input**: 
  - `field` (str): The field name to apply the "not in" condition on.
  - `value` (List[Any]): The list of values to compare the field against.
- **Output**: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the "not in" condition.

```python
def _not_in(field: str, value: List[Any]) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L189)

### `create_search_query`

Creates a search query from the given field and value.

- **Input**: 
  - `field` (str): The field name to apply the search query on.
  - `value` (Any): The value to search for in the specified field.
- **Output**: 
  - `SearchQuery`: A Couchbase-compatible search query object.

```python
def create_search_query(field: str, value: Any) -> SearchQuery:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L203)

### `_parse_comparison_condition`

Parses comparison conditions in filters.

- **Input**: 
  - `condition` (Dict[str, Any]): A dictionary representing the comparison condition to parse.
- **Output**

: 
  - `Dict[str, Any]`: A Couchbase-compatible search query object representing the comparison condition.

```python
def _parse_comparison_condition(condition: Dict[str, Any]) -> Dict[str, Any]:
    # Function body...
```

[Source on GitHub](https://github.com/your-repo/your-project/blob/main/path/to/your/file.py#L221)

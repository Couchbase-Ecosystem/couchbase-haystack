# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import pytest
from typing import Dict, Any

from couchbase_haystack.document_stores.sql_filters import normalize_sql_filters


class TestSQLFiltersIntegration:
    """Integration tests for SQL++ filter normalization with real-world scenarios"""

    def test_document_metadata_filter(self):
        """Test filtering documents by nested metadata fields"""
        # A filter combining multiple metadata conditions
        filter_dict = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.year", "operator": ">=", "value": 2020},
                {"field": "metadata.author", "operator": "==", "value": "Jane Doe"},
                {"field": "metadata.published", "operator": "==", "value": True}
            ]
        }

        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Build a sample query
        query = f"SELECT * FROM documents WHERE {sql_filter}"
        
        # Check expected SQL++ query
        expected = "SELECT * FROM documents WHERE (metadata.`year` >= 2020 AND metadata.`author` = 'Jane Doe' AND metadata.`published` = true)"
        assert query == expected

    def test_vector_search_with_metadata_filter(self):
        """Test vector search with metadata filtering"""
        # A filter for combining vector search with metadata filtering
        filter_dict = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.category", "operator": "in", "value": ["science", "technology"]},
                {"field": "metadata.min_age", "operator": "<=", "value": 18}
            ]
        }
        
        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Build a sample vector search query (simplified)
        query_vector = "[0.1, 0.2, 0.3]"  # Just an example vector
        query = f"""
        SELECT *
        FROM documents
        WHERE {sql_filter}
        ORDER BY VECTOR_DISTANCE(embedding, {query_vector}, "COSINE")
        LIMIT 10
        """
        
        # Check that the filter is correctly incorporated
        assert "WHERE (metadata.`category` IN ['science', 'technology'] AND metadata.`min_age` <= 18)" in query.replace("\n", " ")

    def test_complex_logical_operations(self):
        """Test complex combination of logical operations"""
        # A complex filter with nested logical operations
        filter_dict = {
            "operator": "OR",
            "conditions": [
                # Premium content
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "metadata.premium", "operator": "==", "value": True},
                        {"field": "metadata.rating", "operator": ">=", "value": 4.5}
                    ]
                },
                # Free content with high engagement
                {
                    "operator": "AND",
                    "conditions": [
                        {"field": "metadata.premium", "operator": "==", "value": False},
                        {
                            "operator": "OR",
                            "conditions": [
                                {"field": "metadata.views", "operator": ">", "value": 10000},
                                {"field": "metadata.likes", "operator": ">", "value": 1000}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Build a sample query
        query = f"SELECT * FROM documents WHERE {sql_filter}"
        
        # Check expected SQL++ query (wrapped for readability)
        expected = """
        SELECT * FROM documents WHERE 
        ((metadata.`premium` = true AND metadata.`rating` >= 4.5) OR 
        (metadata.`premium` = false AND (metadata.`views` > 10000 OR metadata.`likes` > 1000)))
        """
        
        # Remove whitespace for comparison
        expected_no_whitespace = "".join(expected.split())
        query_no_whitespace = "".join(query.split())
        
        assert query_no_whitespace == expected_no_whitespace

    def test_date_filtering(self):
        """Test filtering with date fields"""
        # A filter using date comparisons
        start_date = "2023-01-01T00:00:00"
        end_date = "2023-12-31T23:59:59"
        
        filter_dict = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.created_at", "operator": ">=", "value": start_date},
                {"field": "metadata.created_at", "operator": "<=", "value": end_date},
                {"field": "metadata.is_archived", "operator": "!=", "value": True}
            ]
        }
        
        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Build a sample query
        query = f"SELECT * FROM documents WHERE {sql_filter}"
        
        # Check expected SQL++ query
        expected = f"SELECT * FROM documents WHERE (metadata.`created_at` >= '{start_date}' AND metadata.`created_at` <= '{end_date}' AND metadata.`is_archived` != true)"
        assert query == expected

    def test_deeply_nested_fields(self):
        """Test filtering with deeply nested document fields"""
        filter_dict = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.stats.views.total", "operator": ">", "value": 1000},
                {"field": "metadata.stats.shares.facebook", "operator": ">", "value": 100},
                {"field": "metadata.stats.comments.count", "operator": ">", "value": 50}
            ]
        }
        
        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Build a sample query
        query = f"SELECT * FROM documents WHERE {sql_filter}"
        
        # Check expected SQL++ query
        expected = "SELECT * FROM documents WHERE (metadata.`stats`.`views`.`total` > 1000 AND metadata.`stats`.`shares`.`facebook` > 100 AND metadata.`stats`.`comments`.`count` > 50)"
        assert query == expected

    def test_combining_with_full_text_search(self):
        """Test combining SQL++ filters with full-text search (simulated)"""
        # Metadata filter
        filter_dict = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.language", "operator": "==", "value": "en"},
                {"field": "metadata.content_type", "operator": "==", "value": "article"}
            ]
        }
        
        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Simulate a full-text search query combined with metadata filtering
        # Note: The actual FTS syntax would depend on Couchbase's implementation
        fts_condition = "SEARCH(content, 'machine learning', {'fuzziness': 1})"
        query = f"""
        SELECT *
        FROM documents
        WHERE {sql_filter} AND {fts_condition}
        ORDER BY score DESC
        LIMIT 20
        """
        
        # Check the filter is correctly incorporated
        expected_filter = "(metadata.`language` = 'en' AND metadata.`content_type` = 'article')"
        assert expected_filter in query.replace("\n", " ")
        assert fts_condition in query

    def test_null_handling(self):
        """Test filtering with NULL values"""
        # Filter for documents with missing tags and a specific status
        filter_dict = {
            "operator": "AND",
            "conditions": [
                {"field": "metadata.tags", "operator": "==", "value": None},
                {"field": "status", "operator": "==", "value": "published"}
            ]
        }
        
        # Convert to SQL++ filter
        sql_filter = normalize_sql_filters(filter_dict)
        
        # Build a sample query
        query = f"SELECT * FROM documents WHERE {sql_filter}"
        
        # Check expected SQL++ query
        expected = "SELECT * FROM documents WHERE (metadata.`tags` IS NULL AND status = 'published')"
        assert query == expected
        
        # Test NOT NULL
        filter_dict["conditions"][0]["operator"] = "!="
        sql_filter = normalize_sql_filters(filter_dict)
        query = f"SELECT * FROM documents WHERE {sql_filter}"
        expected = "SELECT * FROM documents WHERE (metadata.`tags` IS NOT NULL AND status = 'published')"
        assert query == expected

    def test_array_contains_equivalent(self):
        """Test filtering equivalent to checking if an array contains a value"""
        # In SQL++, we can simulate "array contains" using the IN operator
        # Filter for documents with specific tag
        tag = "important"
        filter_dict = {
            "field": tag, 
            "operator": "in", 
            "value": ["metadata.tags"]
        }
        
        # This would need special handling in the application code
        # as this isn't directly supported in the filter system
        # Here's how a manual SQL++ query might look:
        manual_query = f"SELECT * FROM documents WHERE '{tag}' IN metadata.tags"
        
        # The structure above doesn't map to our filter system, so this test
        # demonstrates a limitation that would need application-level handling 
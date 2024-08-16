from couchbase_haystack.document_stores.filters import _normalize_filters
import pytest
from haystack.errors import FilterError

@pytest.mark.unit
class TestFilterEq:
    def test_filter_eq_condition_str(self):
       filter = {"field": "meta.years", "operator": "==", "value": "2019"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'match': '2019'}

    def test_filter_eq_condition_number(self):
       filter = {"field": "meta.years", "operator": "==", "value": 2019}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'min': 2019, "max": 2019, "inclusive_max": True, "inclusive_min": True }   

    def test_filter_eq_condition_date(self):
       filter = {"field": "meta.years", "operator": "==", "value": "2011-10-05T14:48:00.000Z"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", "end": "2011-10-05T14:48:00.000Z", "inclusive_start": True, "inclusive_end": True }      

    def test_filter_eq_condition_array_of_str(self):
       filter = {"field": "meta.years", "operator": "==", "value": ["1", "2"]}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must': {
                'conjuncts':[
                    {'field': 'meta.years', "match": "1" }, 
                    {'field': 'meta.years', "match": "2"}
                ] 
            }
        }

    def test_filter_eq_condition_array_of_date(self):
       filter = {"field": "meta.years", "operator": "==", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must': {
                'conjuncts':[
                    {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", "end": "2011-10-05T14:48:00.000Z", "inclusive_start": True, "inclusive_end": True }, 
                    {'field': 'meta.years', 'start': "2011-10-05T14:49:00.000Z", "end": "2011-10-05T14:49:00.000Z", "inclusive_start": True, "inclusive_end": True}
                ] 
            }
        } 

    def test_filter_eq_condition_array_of_number(self):
       filter = {"field": "meta.years", "operator": "==", "value": [1, 2]}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must': {
                'conjuncts':[
                    {'field': 'meta.years', 'min': 1, "max": 1, "inclusive_min": True, "inclusive_max": True }, 
                    {'field': 'meta.years', 'min': 2, "max": 2, "inclusive_min": True, "inclusive_max": True}
                ] 
            }
        } 

@pytest.mark.unit
class TestFilterNeq:
    def test_filter_neq_condition_str(self):
       filter = {"field": "meta.years", "operator": "!=", "value": "2011"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must_not': {
                'min': 1,
                'disjuncts':[
                    {'field': 'meta.years', "match": "2011" }
                ] 
            }
        }
    def test_filter_neq_condition_date(self):
       filter = {"field": "meta.years", "operator": "!=", "value": "2011-10-05T14:48:00.000Z"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must_not': {
                'min': 1,
                'disjuncts':[
                    {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", "end": "2011-10-05T14:48:00.000Z", "inclusive_start": True, "inclusive_end": True }
                ] 
            }
        }

    def test_filter_neq_condition_number(self):
       filter = {"field": "meta.years", "operator": "!=", "value": 1}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {
          'must_not': {
                'min': 1,
                'disjuncts':[
                    {'field': 'meta.years', 'min': 1, "max": 1, "inclusive_min": True, "inclusive_max": True }
                ] 
            }
        }        

    def test_filter_neq_condition_array_str(self):
       filter = {"field": "meta.years", "operator": "!=", "value": ["2011", "2012"]}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must_not': {
                'min': 2,
                'disjuncts':[
                    {'field': 'meta.years', 'match': '2011' }, 
                    {'field': 'meta.years', "match": '2012'}
                ] 
            }
        }

    def test_filter_neq_condition_array_date(self):
       filter = {"field": "meta.years", "operator": "!=", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must_not': {
                'min': 2,
                'disjuncts':[
                    {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", "end": "2011-10-05T14:48:00.000Z", "inclusive_start": True, "inclusive_end": True }, 
                    {'field': 'meta.years', 'start': "2011-10-05T14:49:00.000Z", "end": "2011-10-05T14:49:00.000Z", "inclusive_start": True, "inclusive_end": True}
                ] 
            }
        }

    def test_filter_neq_condition_array_number(self):
       filter = {"field": "meta.years", "operator": "!=", "value": [2011, 2012]}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == { 
          'must_not': {
                'min': 2,
                'disjuncts':[
                    {'field': 'meta.years', 'min': 2011, "max": 2011, "inclusive_min": True, "inclusive_max": True }, 
                    {'field': 'meta.years', 'min': 2012, "max": 2012, "inclusive_min": True, "inclusive_max": True}
                ] 
            }
        }    

@pytest.mark.unit
class TestFilterLT:
    # def test_filter_gt_condition_str(self):
    #    filter = {"field": "meta.years", "operator": "==", "value": "2019"}
    #    normalized_filter = _normalize_filters(filter)
    #    assert normalized_filter.encodable == {'field': 'meta.years', 'match': '2019'}

    def test_filter_lt_condition_number(self):
       filter = {"field": "meta.years", "operator": "<", "value": 2019}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'max': 2019}   

    def test_filter_lt_condition_date(self):
       filter = {"field": "meta.years", "operator": "<", "value": "2011-10-05T14:48:00.000Z"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'end': "2011-10-05T14:48:00.000Z" }      

    def test_filter_lt_condition_array_of_str(self):
       filter = {"field": "meta.years", "operator": "<", "value": ["1", "2"]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_lt_condition_array_of_date(self):
       filter = {"field": "meta.years", "operator": "<", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_lt_condition_array_of_number(self):
       filter = {"field": "meta.years", "operator": "<", "value": [1, 2]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"


@pytest.mark.unit
class TestFilterLTE:
   
    # def test_filter_gt_condition_str(self):
    #    filter = {"field": "meta.years", "operator": "==", "value": "2019"}
    #    normalized_filter = _normalize_filters(filter)
    #    assert normalized_filter.encodable == {'field': 'meta.years', 'match': '2019'}

    def test_filter_lte_condition_number(self):
       filter = {"field": "meta.years", "operator": "<=", "value": 2019}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'max': 2019, "inclusive_max": True}   

    def test_filter_lte_condition_date(self):
       filter = {"field": "meta.years", "operator": "<=", "value": "2011-10-05T14:48:00.000Z"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'end': "2011-10-05T14:48:00.000Z", "inclusive_end": True }      

    def test_filter_lte_condition_array_of_str(self):
       filter = {"field": "meta.years", "operator": "<=", "value": ["1", "2"]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_lte_condition_array_of_date(self):
       filter = {"field": "meta.years", "operator": "<=", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_lte_condition_array_of_number(self):
       filter = {"field": "meta.years", "operator": "<=", "value": [1, 2]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"


@pytest.mark.unit
class TestFilterGT:
    # def test_filter_gt_condition_str(self):
    #    filter = {"field": "meta.years", "operator": "==", "value": "2019"}
    #    normalized_filter = _normalize_filters(filter)
    #    assert normalized_filter.encodable == {'field': 'meta.years', 'match': '2019'}

    def test_filter_gt_condition_number(self):
       filter = {"field": "meta.years", "operator": ">", "value": 2019}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'min': 2019}   

    def test_filter_gt_condition_date(self):
       filter = {"field": "meta.years", "operator": ">", "value": "2011-10-05T14:48:00.000Z"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z" }      

    def test_filter_gt_condition_array_of_str(self):
       filter = {"field": "meta.years", "operator": ">", "value": ["1", "2"]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_gt_condition_array_of_date(self):
       filter = {"field": "meta.years", "operator": ">", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_gt_condition_array_of_number(self):
       filter = {"field": "meta.years", "operator": ">", "value": [1, 2]}
       with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
       assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"


@pytest.mark.unit
class TestFilterGTE:
    # def test_filter_gt_condition_str(self):
    #    filter = {"field": "meta.years", "operator": "==", "value": "2019"}
    #    normalized_filter = _normalize_filters(filter)
    #    assert normalized_filter.encodable == {'field': 'meta.years', 'match': '2019'}

    def test_filter_gte_condition_number(self):
       filter = {"field": "meta.years", "operator": ">=", "value": 2019}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'min': 2019, "inclusive_min": True}   

    def test_filter_gte_condition_date(self):
       filter = {"field": "meta.years", "operator": ">=", "value": "2011-10-05T14:48:00.000Z"}
       normalized_filter = _normalize_filters(filter)
       assert normalized_filter.encodable == {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", "inclusive_start": True }      

    def test_filter_gte_condition_array_of_str(self):
      filter = {"field": "meta.years", "operator": ">=", "value": ["1", "2"]}
      with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
      assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_gte_condition_array_of_date(self):
      filter = {"field": "meta.years", "operator": ">=", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
      with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
      assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"

    def test_filter_gte_condition_array_of_number(self):
      filter = {"field": "meta.years", "operator": ">=", "value": [1, 2]}
      with pytest.raises(FilterError) as ex:
        normalized_filter = _normalize_filters(filter)
      assert str(ex.value) == "Filter value can't be of type <class 'list'> using operators '>', '>=', '<', '<='"



@pytest.mark.unit
class TestFilterIN:
   def test_filter_in_condition_str(self):
      filter = {"field": "meta.years", "operator": "in", "value": ["2019"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
            'should': {
                  'min':1,
                  'disjuncts':[
                     {'field': 'meta.years', 'match': '2019'}
                  ]
            }
      }

   def test_filter_in_condition_number(self):
      filter = {"field": "meta.years", "operator": "in", "value": [2019]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == { 
         'should': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'min': 2019, 'max': 2019, "inclusive_max": True, "inclusive_min": True}
                  ]
         }
      }

   def test_filter_in_condition_date(self):
      filter = {"field": "meta.years", "operator": "in", "value": ["2011-10-05T14:48:00.000Z"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'should': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", 'end':  "2011-10-05T14:48:00.000Z", "inclusive_start": True,  "inclusive_end": True}
                  ]
         }
      }
       

   def test_filter_in_condition_array_of_str(self):
      filter = {"field": "meta.years", "operator": "in", "value": ["1", "2"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'should': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'match': '1'},
                     {'field': 'meta.years', 'match': '2'}
                  ]
         }
      }

   def test_filter_in_condition_array_of_date(self):
      filter = {"field": "meta.years", "operator": "in", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'should': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", 'end':  "2011-10-05T14:48:00.000Z", "inclusive_start": True,  "inclusive_end": True},
                     {'field': 'meta.years', 'start': "2011-10-05T14:49:00.000Z", 'end':  "2011-10-05T14:49:00.000Z", "inclusive_start": True,  "inclusive_end": True}
                  ]
         }
      }

   def test_filter_in_condition_array_of_number(self):
      filter = {"field": "meta.years", "operator": "in", "value": [1, 2]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == { 
         'should': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'min': 1, 'max': 1, "inclusive_max": True, "inclusive_min": True},
                     {'field': 'meta.years', 'min': 2, 'max': 2, "inclusive_max": True, "inclusive_min": True}
                  ]
         }
      }

@pytest.mark.unit
class TestFilterNIN:
   def test_filter_nin_condition_str(self):
      filter = {"field": "meta.years", "operator": "not in", "value": ["2019"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
            'must_not': {
                  'min':1,
                  'disjuncts':[
                     {'field': 'meta.years', 'match': '2019'}
                  ]
            }
      }

   def test_filter_nin_condition_number(self):
      filter = {"field": "meta.years", "operator": "not in", "value": [2019]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == { 
         'must_not': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'min': 2019, 'max': 2019, "inclusive_max": True, "inclusive_min": True}
                  ]
         }
      }

   def test_filter_nin_condition_date(self):
      filter = {"field": "meta.years", "operator": "not in", "value": ["2011-10-05T14:48:00.000Z"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'must_not': {
                  "min":1,
                  'disjuncts':[
                     {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", 'end':  "2011-10-05T14:48:00.000Z", "inclusive_start": True,  "inclusive_end": True}
                  ]
         }
      }
       

   def test_filter_nin_condition_array_of_str(self):
      filter = {"field": "meta.years", "operator": "not in", "value": ["1", "2"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'must_not': {
                  "min":2,
                  'disjuncts':[
                     {'field': 'meta.years', 'match': '1'},
                     {'field': 'meta.years', 'match': '2'}
                  ]
         }
      }

   def test_filter_nin_condition_array_of_date(self):
      filter = {"field": "meta.years", "operator": "not in", "value": ["2011-10-05T14:48:00.000Z", "2011-10-05T14:49:00.000Z"]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'must_not': {
                  "min":2,
                  'disjuncts':[
                     {'field': 'meta.years', 'start': "2011-10-05T14:48:00.000Z", 'end':  "2011-10-05T14:48:00.000Z", "inclusive_start": True,  "inclusive_end": True},
                     {'field': 'meta.years', 'start': "2011-10-05T14:49:00.000Z", 'end':  "2011-10-05T14:49:00.000Z", "inclusive_start": True,  "inclusive_end": True}
                  ]
         }
      }

   def test_filter_nin_condition_array_of_number(self):
      filter = {"field": "meta.years", "operator": "not in", "value": [1, 2]}
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == { 
         'must_not': {
                  "min":2,
                  'disjuncts':[
                     {'field': 'meta.years', 'min': 1, 'max': 1, "inclusive_max": True, "inclusive_min": True},
                     {'field': 'meta.years', 'min': 2, 'max': 2, "inclusive_max": True, "inclusive_min": True}
                  ]
         }
      }   

@pytest.mark.unit
class TestFilterComplex:         
   def test_filter_nin_condition_array_of_number(self):
      filter = {
         "operator": "AND",
         "conditions": [
            {"field": "meta.years", "operator": "in", "value": [1, 2]},
            {"field": "meta.years", "operator": "==", "value": 2019},
            {"field": "meta.date1", "operator": "==", "value": "2011-10-05T14:48:00.000Z"},
            {
               "operator": "OR",
               "conditions": [
                  {"field": "meta.text", "operator": "in", "value": ["1", "2"]},
                  {"field": "meta.date2", "operator": ">=", "value": "2011-10-05T14:48:00.000Z"},
                  {
                     "operator": "NOT",
                     "conditions": [
                        {"field": "meta.date3", "operator": "==", "value": ["2011-10-05T14:48:00.000Z"]},
                     ]   
                  }
               ]  
            }
         ]   
      }
      
      normalized_filter = _normalize_filters(filter)
      assert normalized_filter.encodable == {
         'must': {
            'conjuncts': [
               {
               'should': {
                  'min': 1,
                  'disjuncts': [
                     {
                     'field': 'meta.years',
                     'inclusive_min': True,
                     'inclusive_max': True,
                     'min': 1,
                     'max': 1
                     },
                     {
                     'field': 'meta.years',
                     'inclusive_min': True,
                     'inclusive_max': True,
                     'min': 2,
                     'max': 2
                     }
                  ]
               }
               },
               {
               'field': 'meta.years',
               'inclusive_min': True,
               'inclusive_max': True,
               'min': 2019,
               'max': 2019
               },
               {
               'field': 'meta.date1',
               'inclusive_start': True,
               'inclusive_end': True,
               'start': '2011-10-05T14:48:00.000Z',
               'end': '2011-10-05T14:48:00.000Z'
               },
               {
               'should': {
                  'min': 1,
                  'disjuncts': [
                     {
                     'should': {
                        'min': 1,
                        'disjuncts': [
                           {
                           'field': 'meta.text',
                           'match': '1'
                           },
                           {
                           'field': 'meta.text',
                           'match': '2'
                           }
                        ]
                     }
                     },
                     {
                     'field': 'meta.date2',
                     'start': '2011-10-05T14:48:00.000Z',
                     'inclusive_start': True
                     },
                     {
                     'must_not': {
                        'min': 1,
                        'disjuncts': [
                           {
                           'must': {
                              'conjuncts': [
                                 {
                                 'field': 'meta.date3',
                                 'inclusive_start': True,
                                 'inclusive_end': True,
                                 'start': '2011-10-05T14:48:00.000Z',
                                 'end': '2011-10-05T14:48:00.000Z'
                                 }
                              ]
                           }
                           }
                        ]
                     }
                     }
                  ]
               }
               }
            ]
         }
      }
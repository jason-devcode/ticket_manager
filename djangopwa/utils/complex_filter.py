from django.db.models import Q as ComplexConditionalFilter
from typing import List

def build_complex_filter(conditions_list: List[dict]) -> ComplexConditionalFilter:
    """
    Build a complex filter object using the conditions list provided.

    This function takes a list of dictionaries, where each dictionary represents 
    a set of conditions to be applied to a Django QuerySet. It combines these 
    conditions using the OR (`|`) operator to create a single complex filter.

    Args:
        conditions_list (List[dict]): A list of dictionaries that contain the 
                                      model field conditions.

    Returns:
        ComplexConditionalFilter: A complex filter object that can be used with 
                                  Django QuerySets.
    """
    # Initialize an empty Q object to store the complex filter
    complex_filter: ComplexConditionalFilter = ComplexConditionalFilter()
    
    # Iterate through each set of conditions in the list
    for conditions in conditions_list:
        # Initialize an empty Q object for the current set of conditions
        filter = ComplexConditionalFilter()
        
        # Iterate through each field-value pair in the current set of conditions
        for field, value in conditions.items():
            # Update the filter with the current condition using the AND operator
            filter &= ComplexConditionalFilter(**{field: value})
        
        # Combine the current filter with the complex filter using the OR operator
        complex_filter |= filter
    
    # Return the combined complex filter
    return complex_filter

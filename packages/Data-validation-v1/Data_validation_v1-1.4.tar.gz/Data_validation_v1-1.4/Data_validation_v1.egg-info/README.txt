Data validation
===========

This package provides a collection of data validation methods. You might find
it most useful for tasks involving <cleaning>,  <investigating>  and also <manipulating> a Pandas dataframe. Typical usage
often looks like this::

    #!/usr/bin/env python

    **Example**		
    from data_validation import data_validation as dv
    
    test = dv.ValidateData(dataframe, "dataframe")
    test.cleaner('GEOID', new_col_name='US', toFind='US', toReplace='DE')
    test.for_duplicates()
    




Functionality
=========



* checks for row and column duplicates

* % ratio of null in a dataframe

* data types in a Series

* info report on dataframe/Series

*finds a string, replaces it and produces the result as a new field

*finds a string and adds a column of the boolean result

*summary statistics and measures of central tendency check

*Value length verification

*Outlier Analysis



Methods Names 
-------------



*for_duplicates

*for_col_nulls

*for_nulls

*data_types_check

*general_report

*cleaner

*summary_stats

*mean_med_factor

*get_truth

*find_string

*Add_column_from_string

*verify_length

*outliers_calculator

*outlier_report



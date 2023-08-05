import pandas as pd
import numpy as np
from distutils.core import setup
from setuptools import setup


class ValidateData(object):
    """Data Validation methods takes in a Pandas Table and does the following:
     -> checks for row and column duplicates
     -> % ratio of null in a dataframe
     -> data types in a Series
     -> info report on dataframe/Series
     ->finds a string, replaces it and produces the result as a new field
     -> summary statistics and measures of central tendency check+
     -> Value length verification
     -> Outlier Analysis
  """

    def __init__(self, df, name):
        """try a pandas attribute on the dataframe, else convert to pandas"""
        try:
            self.df = df
            df.any()
        except AttributeError:
            self.df = df.toPandas()

        self.name = name

        if self.df.empty:
            raise Exception('Empty Dataset')

    def for_duplicates(self):
        """
        loops over the dataframe
        :return: duplicate report for each column
        """
        print('++++++++++++ Duplicates Check Start+++++++++++++')
        print('Report for:', self.name)
        if not self.df.empty:
            for column in self.df.columns:
                if self.df.duplicated(column).sum() > 0:
                    print('Duplicates found in: ', column)
                else:
                    print('No duplicates found in: ', column)
        else:
            print('Empty data set')
        print('++++++++++++ Duplicates Check End+++++++++++++')

    def for_col_nulls(self, col_name, threshold=0.01):
        """
        :param col_name: column name
        :param threshold: % of nulls acceptable in dataframe. Default = 1%
        :return: report based on threshold set
        """
        print('++++++++++++ Nulls Check Start+++++++++++++')
        print('Report for:', col_name)
        if self.df[[col_name]].isna().sum().values.sum() >= int(self.df.size) * threshold:
            print('Over', threshold, 'threshold of the data contains Nulls')
        else:
            print('Below threshold of nulls')
        print('++++++++++++ Null Check End+++++++++++++')

    def for_nulls(self, threshold=0.01):
        """
        :param threshold: % of nulls acceptable in dataframe. Default = 1%
        :return: report based on threshold set
        """
        print('++++++++++++ Nulls Check Start+++++++++++++')
        print('Report for:', self.name)
        if self.df.isna().sum().values.sum() >= int(self.df.size) * threshold:
            print('Over', threshold, 'threshold of the data contains Nulls')
        else:
            print('Below threshold of nulls')
        print('++++++++++++ Null Check End+++++++++++++')

    def data_types_check(self, col_name):
        """
        :param col_name: column name
        :return: returns the datatypes within a series
        """
        print('++++++++++++ Data Types Check Start+++++++++++++')
        print('Report for:', col_name)
        if not self.df.empty:
            if int(self.df[[col_name]].applymap(type).nunique()) == 1:
                print('Only One data type found')
            else:
                print('Multiple data types:', self.df[[col_name]].applymap(type)[col_name].unique())
        else:
            print('empty data set')
        print('++++++++++++ Data types Check End+++++++++++++')

    def general_report(self, col_name=None):
        """
        :param col_name: Series, if not provided, will perform operation for the whole dataframe
        :return: Report
        """
        print('++++++++++++ General Report Start+++++++++++++')
        print('Report for:', self.name, col_name)
        if not self.df.empty:
            if col_name is not None:
                for i in [col_name]:
                    try:
                        print('info report', dict(self.df[[str(i)]].info()))
                    except TypeError:
                        print('Data Rows: Total', self.df[str(col_name)].shape[0], 'Rows')
            else:
                try:
                    print('info report', dict(self.df.info()))
                except TypeError:
                    print('Data Rows: Total', self.df.shape[0], 'Rows')
        else:
            print('Empty data set')
        print('++++++++++++General Report End+++++++++++++')

    def cleaner(self, col_name, new_col_name, to_find, to_replace):
        """
        create a clean new column after finding the string and replacing it
        :param col_name:
        :param new_col_name:
        :param to_find:
        :param to_replace:
        :return: df with new_col_name
        """
        print('++++++++++++Cleaner Start+++++++++++++')
        print('Cleaning:', col_name, ' Created New Column:', new_col_name)
        if not self.df.empty:
            try:
                self.df[new_col_name] = self.df[col_name].str.replace(str(to_find), str(to_replace))
            except ValueError as e:
                print(e)
        else:
            print('empty data set')
        print('++++++++++++Cleaner End+++++++++++++')

    def summary_stats(self, col_name):
        """
            :param col_name: integer series
            :return: measure of central tendencies
            """
        print('++++++++++++Summary Statistics Start+++++++++++++')
        if not self.df.empty:
            try:
                mean = self.df[str(col_name)].mean()
                median = self.df[str(col_name)].median()
                print('Report for:', col_name)
                print('Min:', (self.df[str(col_name)].min()))
                print('Max:', self.df[str(col_name)].max())
                print('Unique values:', self.df[str(col_name)].nunique(), 'of', len(self.df[str(col_name)]))
                print('Mean:', mean)
                print('Median', median)
                print('Skew:', self.df[str(col_name)].skew())
                print('var:', self.df[str(col_name)].var())
                print('standard_deviation:', self.df[str(col_name)].std())
                print('', ValidateData.mean_med_factor(self.df, col_name))
            except ValueError:
                print('Wrong value types in Column')
            except TypeError:
                print('Wrong value types in Column')
        else:
            print('empty data set')
        print('++++++++++++Summary Statistics End+++++++++++++')

    @staticmethod
    def mean_med_factor(df, col):
        if not df.empty:
            mean = df[str(col)].mean()
            median = df[str(col)].median()
            x = mean / median
            if x > 1:
                print('Possible Outliers on the right,', 'Factor:', x - 1,
                      'if the Factor, is high Confirm with Outlier Report')
            else:
                print('Possible Outlier to the left', 'if the Factor is high,  Confirm with Outlier Report')
        else:
            print('empty data set')

    @staticmethod
    def get_truth(vals):
        count = 0
        trues = filter(lambda x: x == True, vals)
        for value in trues:
            count += 1
        return count

    def find_string(self, col_name, val):
        """string matching
            :param col_name: Series you intend to search through
            :param val: string to search for
            """
        print('++++++++++++ Find String Start+++++++++++++')
        print('Implementing for:', col_name)
        if not self.df.empty:
            try:
                my_str = self.df[col_name].str
                condition = (ValidateData.get_truth(my_str.startswith(val).values) > 0 or
                             ValidateData.get_truth(my_str.endswith(val).values) > 0 or
                             ValidateData.get_truth(my_str.match(val).values) > 0 or
                             ValidateData.get_truth(my_str.contains(val).values))
                if condition:
                    print('Match Found at Position:', 'Start', ValidateData.get_truth(my_str.startswith(val).values),
                          'End:', ValidateData.get_truth(my_str.endswith(val).values),
                          'Exact match:', ValidateData.get_truth(my_str.match(val).values),
                          'Total:', ValidateData.get_truth(my_str.contains(val).values)
                          )
                else:
                    print('No Match')
            except AttributeError:
                print('Not a String Column')
        else:
            print('empty data set')
        print('++++++++++++ Find String End+++++++++++++')

    def Add_column_from_string (self,col_name, val, new_col_name):
        """
        :param col_name: column
        :param val: string value to look for 
        :param new_col_name: new column name
        :return: Add a generated Boolean field the dataframe
        """
        print('++++++++++++Add col from String+++++++++++++')
        print('Implementing for:', col_name)
        if not self.df.empty:
            try:
                my_str = self.df[col_name].str
                self.df[new_col_name] = my_str.contains(val)
            except AttributeError:
                print('Not a String Column')
        else:
            print('empty data set')
        print('++++++++++++Add col from String+++++++++++++')

    def verify_length(self, col_name, default_len):
        """
        :param col_name: column name string
        :param default_len: intergen value to match
        :return: number of mismatches
        """
        print('++++++++++++ Verify Length Start +++++++++++++')
        print('Implementing for:', col_name)
        if not self.df.empty:
            bol = []
            for val in self.df[col_name]:
                if len(str(val)) == default_len:
                    bol.append(True)
                else:
                    bol.append(False)
            Trues = ValidateData.get_truth(bol)
            Total = len(self.df[col_name])
            print('Total Mismatch found: ', Total - Trues)
        else:
            print('empty data set')
        print('++++++++++++ Verify Length End+++++++++++++')

    def outliers_calculator(df, col_name):
        """
        :param col_name: column name
        :return: outlier low end and high end values of a series
        """
        print('++++++++++++ Outlier Check Start+++++++++++++')
        print('Report for:', col_name)
        if not df.empty:
            Quartile_1 = df[[str(col_name)]].quantile(0.25).values
            Quartile_3 = df[[str(col_name)]].quantile(0.75).values
            interquartile_Range = (Quartile_3 - Quartile_1)
            low_end = Quartile_1 - 1.5 * interquartile_Range
            high_end = Quartile_3 + 1.5 * interquartile_Range
            x = [low_end, high_end]
        return low_end, high_end

    def outlier_report(self, col_name):
        """
        :param col_name: column to iterate over
        :return: Total number of outlier found
        """
        if not self.df.empty:
            try:
                bol = []
                x = ValidateData.outliers_calculator(self.df, col_name)
                for val in self.df[str(col_name)]:
                    if val < x[0] or val > x[1]:
                        bol.append(True)
                    else:
                        bol.append(False)
                print('Total Outliers:', ValidateData.get_truth(bol))
            except (ValueError, TypeError):
                print('Wrong value types in Column')
        else:
            print('empty data set')
        print('++++++++++++ Outlier Check End+++++++++++++')

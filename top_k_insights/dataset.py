import pandas as pd


class Dataset:
    def __init__(self, filename):
        """
        Datasets should be csvs formatted with dimension columns to the left
        and measure as the final column. The first row should be a header.
        """
        self.data = pd.read_csv(filename, encoding='mac_roman')
        self.measure = self.data.columns[-1]
        self.dimensions = self.data.columns[:-1]


    def extract(self, subspace, dividing_dimension, extractor):
        """
        subspace is a dict of ('dimension_name':'value') pairs
            for filtered dimensions. Excluding a dimension means no filter.
        extractor is one of ['sum', 'rank', 'delta_prev', 'pct', 'delta_avg']

        TODO: only return single extractor results, not all four.
        """
        # Filter along all subspaces
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace)).all(axis=1)]

        # Group by the dividing dimension
        result_set = subset.groupby(dividing_dimension).\
            agg({self.measure:'sum'})

        # Calculate aggregate measures
        result_set['rank'] = result_set.rank(ascending=False)
        result_set['pct'] = 100 * result_set[self.measure] / result_set[self.measure].sum()
        result_set['delta_avg'] = result_set[self.measure] - result_set[self.measure].sum() / len(result_set)
        result_set = result_set.reset_index()
        if "year" in result_set.columns:
            result_set['delta_prev'] = result_set.sort_values("year")[self.measure].diff() / result_set.sort_values("year")["year"].diff()

        return result_set


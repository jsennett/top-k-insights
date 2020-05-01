import pandas as pd
import numpy as np
import logging
import heapq
import scipy
import scipy.stats


class Dataset:

    def __init__(self, data, measure, dimensions):
        """
        data: pandas dataframe
        measure: string measure name
        dimensions: array of strings of dimension names
        """
        self.data = data
        self.measure = measure
        self.dimensions = dimensions

    @classmethod
    def fromfilename(cls, filename):
        """
        Datasets should be csvs formatted with dimension columns to the left
        and measure as the final column. The first row should be a header.
        """
        data = pd.read_csv(filename, encoding='mac_roman')
        measure = data.columns[-1]
        dimensions = data.columns[:-1]
        return cls(data, measure, dimensions)

    def extract_insights(self, depth, k):
        """ Algorithm 1

        maintain a min-heap of top k insights
        enumerate all composite extractors for depth tao
        for each composite extractor:
            for each dimension of dataset:
                initialize subspace
                enumerate_insight(subspace, dimension, composite extractor)
        return min-heap
        """
        logging.info("Extracting insights for depth: " + str(depth))

        # Reset analysis attributes
        self.top_insights = []
        self.k = k
        self.depth = depth


        # Enumerate all composite extractors for depth 1 or 2
        if depth == 1:
            composite_extractors =  [[("sum", self.measure)]]
        elif depth == 2:
            composite_extractors = []
            for dimension in self.dimensions:
                for extractor in ["rank", "delta_prev", "pct", "delta_avg"]:
                    composite_extractors += [[("sum", self.measure), (extractor, dimension)]]
        else:
            raise ValueError("Expected depth of 1 or 2, not", depth)

        logging.info("Considering composite extractors:")
        for ce in composite_extractors:
            logging.info(ce)

        # Enumerate sibling groups
        for composite_extractor in composite_extractors:
            for dimension in self.dimensions:
                self.enumerate_insight({}, dimension, composite_extractor)

        # TODO: return the topk insights. Maybe write them to file
        return self.top_insights

    def enumerate_insight(self, subspace, dimension, composite_extractor):
        """
        if is_valid(subspace, dimension, composite extractor):
            result_set = extract_result_set(subspace, dimensionm, composite extractor)
            for each insight type:
                score = impact(subspace, dimension) * significance(result_set)
        """
        if self.is_valid(subspace, dimension, composite_extractor):
            logging.info("    Valid SG/CE combo: subspace(%s), dim(%s), ce(%s)" % (subspace, dimension, composite_extractor))

            # extract result set
            result_set = self.extract_result_set(subspace, dimension, composite_extractor)
            if result_set is None or len(result_set) == 0:
                return

            for insight_type in ["point", "shape"]:

                if insight_type == "shape" and dimension != "year":
                    continue

                if insight_type == "shape":
                    significance = self.shape_significance

                elif insight_type == "point":
                    significance = self.point_significance

                # compute insight score
                score = self.impact(subspace, dimension) * significance(result_set)

                # Generate a new insight with info needed to interpret it
                new_insight = Insight(score, subspace, dimension, composite_extractor, insight_type)

                # Update the minheap if the insight has a top k score
                if len(self.top_insights) < self.k:
                    heapq.heappush(self.top_insights, new_insight)
                else:
                    heapq.heappushpop(self.top_insights, new_insight)

        else:
            logging.info("Invalid SG/CE combo: subspace(%s), dim(%s), ce(%s)" % (subspace, dimension, composite_extractor))

        # Enumerate child subspaces
        # TODO: see why some subspaces aren't appearing, like year==2016
        unique_vals = self.data[dimension].unique()
        for value in unique_vals:
            subspace[dimension] = value
            for new_dimension in set(self.dimensions) - set(subspace):
                self.enumerate_insight(subspace, new_dimension, composite_extractor)


    def is_valid(self, subspace, dimension, composite_extractor):
        """
        A composite extractor is invalid iff pct is not the first extractor used.
        With a depth of 2 (and only 1 extractor), this is never a concern.

        A sibling group SG(S, Da) is a valid input for composite extractor Ce iff
        for each pair (E, Dx) in Ce, Dx=Da or S[Dx] != "∗" (all values).

        In addition, the extractor delta_prev is only valid for ordinal dimensions;
        Assume that the only ordinal dimension will be 'year'.
        """
        for (extractor, measure) in composite_extractor[1:]:
            if measure != dimension and subspace.get(measure) is None:
                return False

            if extractor == 'delta_prev' and dimension != 'year':
                return False

        return True


    def impact(self, subspace, dimension):
        """
        The impact score is the market share of the subspace S.
        """
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]

        numerator = subset[self.measure].sum()
        denominator = self.data[self.measure].sum()

        impact_score = float(numerator / denominator)
        assert(0.0 <= impact_score <= 1.0)

        return impact_score


    def shape_significance(self, result_set):
        """
        input: result_set is a dataframe with measure column 'M',
        output: a significance score between [0.0, 1.0]

        Calculating the shape_significance is only relevant when
        the dividing dimension is ordinal. For example, when the
        sibling group uses "year" as its dividing dimension.
        """
        assert("year" in result_set.columns and "M" in result_set.columns)
        slope, intercept, r, p, stderr = scipy.stats.linregress(result_set['year'], result_set['M'])
        return (r**2) * (1 - p)

    def point_significance(self, result_set):
        """
        input: result_set is a dataframe with measure column 'M',
        output: a significance score between [0.0, 1.0]

        To calculate point significance:

            obtain max value from X, X_max
            Fit X - X_max to a power-law distribution
            derive prediction error for x_max: err_max = x_max_pred - x_max
            calculate p value: p = P(e > err_max | N(u, d))
            sig = 1 - p

        To fit power law distribution, convert to an equivalent linear model

            powerlaw:           y = ax^b
            equivalent linear:  log(y) = log(a) + b*log(x)

            In our case, y is the frequency of each x value

        # TODO: also enumerate mininmum point significance
        """
        # With too few data points, we can't actually calculate point sig
        if len(result_set) <= 2:
            return 0.0

        # x_max
        x_max = result_set['M'].max()

        # X \ x_max
        freq = result_set['M'].value_counts()
        freq_x_max = freq[x_max]
        if freq_x_max == 1:
            freq = freq.drop(x_max)
        else:
            freq[x_max] -= 1

        # Fit power law distribution by fitting linear model to log
        logx = np.lib.scimath.log2(freq.index)
        logy = np.lib.scimath.log2(freq)
        slope, intercept, r, p, stderr = scipy.stats.linregress(logx, logy)

        # TODO: cut out parts not needed for p calc
        res = pd.DataFrame(zip(logx, logy, freq.index, freq), columns=['log_num_papers', 'log_freq', 'num_papers', 'freq'])
        res['err_pred_freq'] = 2**(intercept + slope * res['log_num_papers']) - res['freq']

        pred_max_freq = 2**(intercept + slope * np.lib.scimath.log2(x_max))

        # Define error as actual freq minus predicted freq
        err_pred_y_max = freq_x_max - pred_max_freq

        # Assume errors fit a Gaussian distribution
        Z = (err_pred_y_max - res['err_pred_freq'].mean())/res['err_pred_freq'].std()

        # An insight would be that the max value exceeds the predicted max
        # value. In this case, the err_pred_y_max would be positive, based
        # on how we defined the error. So, we should use one-tailed test,
        # only caring about the right tail. A left tail error means that
        # our maximum value was lower than expected, which isn't insightful.
        # cdf(Z) = 1 - p = significance_score
        significance_score = scipy.stats.norm.cdf(Z)

        return significance_score


    def extract_result_set(self, subspace, dividing_dimension, composite_extractor):
        """
        subspace is a dict of ('dimension_name':'value') pairs
            for filtered dimensions. Excluding a dimension means no filter.

        result_set = empty-set
        for val in dividing_dimension:
            subspace[dividing_dimension] = val
            partial_result_set = recur_extract_result_set(subspace, self.depth, composite_extractor)
            partial_result_set['subspace'] = str(subspace) # decode with eval()
            result_set += partial_result_set

        unique_vals = self.data[dimension].unique()
        """
        logging.debug("extract_result_set(%s, %s, %s" % (subspace, dividing_dimension, composite_extractor))

        if self.depth == 1:
            subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]
            result_set = subset.groupby(dividing_dimension).agg({self.measure:'sum'})
            result_set.rename(columns={self.measure:'M'}, inplace=True)

            # Add dimension information back into the result set
            result_set = result_set.reset_index(drop=False)
            for dim in self.dimensions:
                if dim not in result_set.columns:
                    result_set[dim] = subspace.get(dim, "*")

            return result_set

        (extractor, analysis_dimension) = composite_extractor[1]
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]

        # Ensure that delta_prev subset includes previous year even when the
        # subspace excludes it; we need the prev year to be able to
        # calculate delta_prev. Once delta_prev is calculated, exclude the
        # previous year from the result set
        if extractor == 'delta_prev' and 'year' in subspace:
            previous_year_subspace = subspace.copy()
            previous_year_subspace['year'] -= 1
            subset = subset.append(self.data.loc[(self.data[list(previous_year_subspace)] == pd.Series(previous_year_subspace, dtype=object)).all(axis=1)])

        # First level of aggregation: sum of the original measure
        result_set = subset.groupby([dividing_dimension]).agg({self.measure:'sum'})

        # Add dimension information back into the result set
        result_set = result_set.reset_index(drop=False)
        for dim in self.dimensions:
            if dim not in result_set.columns:
                result_set[dim] = subspace.get(dim, "*")


        # Second level of aggregation, implicitly over the analysis_dimension
        if extractor == 'rank':
            result_set['M'] = result_set[self.measure].rank(ascending=False)

        elif extractor == 'pct':
            result_set['M'] = 100 * result_set[self.measure] / sum(result_set[self.measure])
            # result_set['pct'] = 100 * result_set[self.measure] / result_set[self.measure].groupby(dividing_dimension).sum()

        elif extractor == 'delta_avg':
            result_set['M'] = result_set[self.measure] - (result_set[self.measure].sum() / len(result_set))

        elif extractor == 'delta_prev':
            result_set['M'] = result_set.sort_values("year")[self.measure].diff()
            if 'year' in subspace:
                result_set = result_set[result_set['year'] == subspace['year']]

        return result_set


    """
    def recursive_extract_result_set(self, subspace, level, composite_extractor):

        if level == 1:
            subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]
            return sum(subset[self.measure])

        # For level 2 results, calculate the aggregate measure of ce[1]
        # using the sum of the main measure for the subspace, which is one
        # of the siblings of the sibling groups
        (extractor, analysis_dimension) = composite_extractor[level-1]
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]

        # TODO: ensure that for delta_prev, the previous year is not excluded
        # from the subset
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]



        level_result_set = pd.DataFrame()

        unique_vals = self.data[analysis_dimension].unique()
        for val in unique_vals:

            child_subspace = subspace.copy()
            child_subspace[analysis_dimension] = val
            child_subspace['M'] = self.recursive_extract_result_set(child_subspace, level-1, composite_extractor)
            level_result_set.append(child_


        result_set = result_set.append(child_result_set)


        return result_set



        # Filter along all subspaces
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]

        # Group by the dividing dimension
        result_set = subset.groupby(dividing_dimension).agg({self.measure:'sum'})

        # Ignore result sets that are too small
        if len(result_set) < 3:
            return None

        # Calculate aggregate measures
        result_set['rank'] = result_set.rank(ascending=False)
        result_set['pct'] = 100 * result_set[self.measure] / result_set[self.measure].sum()
        result_set['delta_avg'] = result_set[self.measure] - result_set[self.measure].sum() / len(result_set)
        result_set = result_set.reset_index()
        if "year" in result_set.columns:
            result_set['delta_prev'] = result_set.sort_values("year")[self.measure].diff() / result_set.sort_values("year")["year"].diff()

        return result_set
    """

class Insight:

    def __init__(self, score, subspace, dimension, composite_extractor, insight_type):
        self.score = score
        self.subspace = subspace
        self.dimension = dimension
        self.composite_extractor = composite_extractor
        self.insight_type = insight_type

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __eq__(self, other):
        return self.score == other.score

    def __repr__(self):
        """
        TODO:
        Come up with a string representation of an Insight.
        Maybe put this in a different method.
        """
        return """
        <Insight: score = %f,
        subspace = %s,
        dimension = %s,
        composite_extractor = %s,
        insight_type = %s> """ % (self.score, self.subspace, self.dimension,
                                  self.composite_extractor, self.insight_type)

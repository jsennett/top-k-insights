import pandas as pd
import logging
import heapq


class Dataset:

    def __init__(self, filename):
        """
        Datasets should be csvs formatted with dimension columns to the left
        and measure as the final column. The first row should be a header.
        """
        self.data = pd.read_csv(filename, encoding='mac_roman')
        self.measure = self.data.columns[-1]
        self.dimensions = self.data.columns[:-1]

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
            result_set = None # Placeholder; extract result_set by appling CE to SG(S, Dx)
            score = self.impact(subspace, dimension) * self.significance(result_set)

            # Generate a new insight with info needed to interpret it
            new_insight = Insight(score, subspace, dimension, composite_extractor)

            # Update the minheap if the insight has a top k score
            if len(self.top_insights) < self.k:
                heapq.heappush(self.top_insights, new_insight)
            else:
                heapq.heappushpop(self.top_insights, new_insight)

        else:
            logging.info("Invalid SG/CE combo: subspace(%s), dim(%s), ce(%s)" % (subspace, dimension, composite_extractor))

        # Enumerate child subspaces
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
        """
        for (extractor, measure) in composite_extractor[1:]:
            if measure != dimension and subspace.get(measure) is None:
                return False
        return True


    def impact(self, subspace, dimension):
        """
        """
        import random
        return random.randint(0,100) / 100 # placeholder


    def significance(self, result_set):
        """
        """
        import random
        return random.randint(0,100) / 100 # placeholder


    def extract_result_set(self, subspace, dividing_dimension, extractor):
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

class Insight:

    def __init__(self, score, subspace, dimension, composite_extractor):
        self.score = score
        self.subspace = subspace
        self.dimension = dimension
        self.composite_extractor = composite_extractor

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
        composite_extractor = %s> """ % (self.score, self.subspace,
                                         self.dimension, self.composite_extractor)

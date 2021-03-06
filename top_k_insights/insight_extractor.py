import pandas as pd
import logging
import heapq

import significance_tests as st


class InsightExtractor:

    def __init__(self, data, dimensions, measure, agg):
        """
        input:
            data: pandas dataframe
            dimensions: array of strings of dimension names
            measure: string measure name
            agg: string of the level-1 aggregation function
                to apply (one of: [sum, count]), default "sum"
        """
        self.data = data.fillna('')
        self.dimensions = dimensions
        self.agg = agg

        # If the aggregate measure is count, create a column of 1s
        # as our measure column. This allows us to use the same 'sum'
        # aggregate functions in place of count
        if self.agg == 'count':
            self.measure = 'count'
            self.data['count'] = 1
        else:
            self.measure = measure

        # Cache the overall sum of the measure, since we use it repeatedly
        self.total_measure_sum = self.data[self.measure].sum()

        # A cutoff score: don't look for insights that have a subgroup impact
        # smaller than this cutoff score.
        self.cutoff = 0.01

        # Starting Insight id, unique for each insight found
        self.iid = 1001

    @classmethod
    def fromfilename(cls, filename, agg):
        """
        Datasets should be csvs formatted with dimension columns to the left
        and measure as the final column. The first row should be a header.
        """
        data = pd.read_csv(filename, encoding='mac_roman')
        measure = data.columns[-1]
        dimensions = data.columns[:-1]
        return cls(data, measure, dimensions, agg)

    def extract_insights(self, depth, k):
        """
        Algorithm 1: Extract Insights

        maintain a min-heap of top k insights
        enumerate all composite extractors for depth tao
        for each composite extractor:
            for each dimension of dataset:
                initialize subspace
                enumerate_insight(subspace, dimension, composite extractor)
        return min-heap
        """

        # Reset analysis attributes
        self.top_insights = []
        self.k = k
        self.depth = depth

        # Enumerate all composite extractors for depth 1 or 2
        if depth == 1:
            composite_extractors =  [[(self.agg, self.measure)]]
        elif depth == 2:
            composite_extractors = []
            for dimension in self.dimensions:
                for extractor in ["rank", "delta_prev", "pct", "delta_avg"]:
                    composite_extractors += [[(self.agg, self.measure), (extractor, dimension)]]
        else:
            raise ValueError("Expected depth of 1 or 2, not", depth)

        # Enumerate sibling groups, extracting insights for each.
        # Start with the subspace of the whole datsaet
        subspace = {}
        for composite_extractor in composite_extractors:
            for dimension in self.dimensions:
                self.enumerate_insight(subspace.copy(), dimension, composite_extractor)

        return self.top_insights

    def enumerate_insight(self, subspace, dimension, composite_extractor):
        """
        Algorithm 1 subroutine: Enumerate Insights

        if is_valid(subspace, dimension, composite extractor):
            result_set = extract_result_set(subspace, dimension, composite extractor)
            for each insight type:
                score = impact(subspace, dimension) * significance(result_set)
        """
        print("enumerate_insight(%s, %s, %s)" % (subspace, dimension, composite_extractor))
        logging.info("enumerate_insight(%s, %s, %s)" % (subspace, dimension, composite_extractor))

        # Impact Upper Bound Optimization:
        # only check for insights if the impact of the subspace
        # exceeds the score of the top kth insight, since this is an upper
        # bound on the insight score. All child subspaces can also be skipped.
        impact = self.impact(subspace, dimension)
        if impact <= self.cutoff or (len(self.top_insights) == self.k
                                     and impact <= self.top_insights[0].score):
            logging.info("Skipping low impact subspace ( %0.2fpct ) - %s" % (impact*100, subspace))
            return

        # Skip if the sibling group and composite extractor are not compatible
        if not self.is_valid(subspace, dimension, composite_extractor):
            logging.info("Invalid SG/CE combo: subspace(%s), dim(%s), ce(%s)" %
                         (subspace, dimension, composite_extractor))
        else:
            logging.info("Valid SG/CE combo: subspace(%s), dim(%s), ce(%s)" %
                         (subspace, dimension, composite_extractor))

            # Extract result set
            result_set = self.extract_result_set(subspace.copy(), dimension, composite_extractor)

            # Don't measure insight scores for result sets with 3 or fewer
            # points; significance tests are not good fits for such little data
            if len(result_set) <= 3:
                logging.info("result_set is too small to consider!")

            else:
                logging.info("RESULT SET:\n %s" % result_set.head(30))
                logging.info("(%s rows)" % len(result_set))

                # Enumerate over each insight type
                for insight_type in ["point", "shape"]:

                    # Skip shape insights unless we have an ordinal dimension
                    if insight_type == "shape" and dimension != "year":
                        continue

                    # Lookup which significance test to use
                    # This depends on the insight type, dimension,
                    # and which extractors are used
                    sigtest = st.get_distribution(insight_type, dimension, self.depth, composite_extractor)
                    insight, significance_score = sigtest(result_set)
                    insight_score = impact * significance_score
                    logging.info("  *  Tested using %s - sig={%0.2f}, impact={%0.2f}, score={%0.2f}" % (sigtest.__name__, significance_score, impact, insight_score))

                    # Generate a new insight with info needed to interpret it
                    new_insight = Insight(self.iid, insight, insight_score, subspace.copy(), dimension, composite_extractor, insight_type, significance_score, sigtest.__name__, impact)
                    self.iid += 1
                    logging.info("INSIGHT FOUND: {}".format(new_insight.interpretation()))
                    print("INSIGHT FOUND: {}".format(new_insight.interpretation()))

                    # Update the minheap if the insight has a top k score
                    if len(self.top_insights) < self.k:
                        heapq.heappush(self.top_insights, new_insight)
                        logging.info("added insight: %s" % new_insight)
                    else:
                        if new_insight.score > self.top_insights[0]:
                            logging.info("added insight: %s" % new_insight)
                        heapq.heappushpop(self.top_insights, new_insight)

        # Since certian  dimensions have zero or only one sizeable unique val,
        # don't enumerate over the child subspaces of the infrequent values.
        # The subspaces will be very low impact and will therefore have low
        # insight scores which will not make it to the top-k scores
        if dimension == 'venue_name':
            unique_vals = ['CoRR']
        elif dimension == 'school':
            unique_vals = ['']
        elif dimension == "paperid" or dimension == "authid":
            unique_vals = []
        else:
            unique_vals = self.data[dimension].unique()

        # Enumerate child subspaces
        for value in unique_vals:
            child_subspace = subspace.copy()
            child_subspace[dimension] = value
            for new_dimension in set(self.dimensions) - set(child_subspace):
                self.enumerate_insight(child_subspace, new_dimension, composite_extractor)


    def extract_result_set(self, subspace, dividing_dimension, composite_extractor):
        """
        Algorithm 2: Build a result set

        result_set = empty-set
        for val in dividing_dimension:
            subspace[dividing_dimension] = val
            partial_result_set = recur_extract_result_set(subspace, self.depth, composite_extractor)
            result_set += partial_result_set

        unique_vals = self.data[dimension].unique()
        """
        logging.info("extract_result_set(%s, %s, %s" % (subspace, dividing_dimension, composite_extractor))

        # Since we only handle depth 1 or 2, I just handle those two cases
        # separately rather than recursively.
        if self.depth == 1:

            subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]
            result_set = subset.groupby(dividing_dimension).agg({self.measure:'sum'}).rename(columns={self.measure:'M'})

            # Add dimension information back into the result set
            result_set = result_set.reset_index(drop=False)
            for dim in self.dimensions:
                if dim not in result_set.columns:
                    result_set[dim] = subspace.get(dim, "*")

            return result_set[result_set['M'].notnull()]


        # There are two possibilities for valid CE/SG combos:
        # 1) the extractor analysis_dimension == dividing_dimension
        # 2) the extractor analysis_dimension != dividing_dimension but
        #    the subspace contains a certain value for analysis_dimension

        # Case 1: just filter to the subset, aggregate by
        # dividing_dimension, agg(sum), and then calculate measure using the
        # extractor over agg(sum) (e.g. rank, delta_prev, pct, delta_avg).
        (extractor, analysis_dimension) = composite_extractor[1]
        if analysis_dimension == dividing_dimension:
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
            result_set = subset.groupby(dividing_dimension).agg({self.measure:'sum'})

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
            elif extractor == 'delta_avg':
                result_set['M'] = result_set[self.measure] - (result_set[self.measure].sum() / len(result_set))
            elif extractor == 'delta_prev':
                result_set['M'] = result_set.sort_values("year")[self.measure].diff()
                if 'year' in subspace:
                    result_set = result_set[result_set['year'] == subspace['year']]

            # exclude null values; these can be common, for example
            # during delta_prev if no prev year is available
            return result_set[result_set['M'].notnull()]

        # Case 2: in this case, we are aggregating over both
        # the analysis dimension and the dividing dimension. Then, we are
        # filtering to only contain the subspace value for that dimension.
        # As a result, we will then have a result for each value in the
        # dividing dimension and a single known value for the analysis
        # dimension.
        else:

            # The temp subset should ignore the subspace value of the
            # analysis_dimension since it is needed to compute the agg measure
            temp_subspace = subspace.copy()
            del temp_subspace[analysis_dimension]

            subset = self.data.loc[(self.data[list(temp_subspace)] == pd.Series(temp_subspace, dtype=object)).all(axis=1)]

            # First level of aggregation: sum of the original measure
            result_set = subset.groupby([dividing_dimension, analysis_dimension]).agg({self.measure:'sum'})

            # Add dimension information back into the result set
            result_set = result_set.reset_index(drop=False)
            for dim in self.dimensions:
                if dim not in result_set.columns:
                    result_set[dim] = subspace.get(dim, "*")

            # Second level of aggregation over the dividing dimension
            if extractor == 'rank':
                result_set['M'] = result_set.groupby(dividing_dimension)[self.measure].rank(ascending=False, method='first')
            elif extractor == 'pct':
                group_sum = result_set.rename(columns={self.measure:'M'}).groupby(dividing_dimension).sum()['M']
                result_set = result_set.merge(group_sum, on=dividing_dimension)
                result_set['M'] = 100 * result_set[self.measure] / result_set['M']
            elif extractor == 'delta_avg':
                group_avg = result_set.rename(columns={self.measure:'M'}).groupby(dividing_dimension).mean()['M']
                result_set = result_set.merge(group_avg, on=dividing_dimension)
                result_set['M'] = result_set[self.measure] - result_set['M']
            elif extractor == 'delta_prev':
                # We only need to consider for the subspace year and the
                # previous year, since 'year' is the only ordinal column
                result_set = result_set[(result_set['year'] == subspace['year']) | (result_set['year'] == subspace['year'] - 1)]
                group_delta_prev = (result_set[result_set['year'] == subspace['year']].rename(columns={self.measure:'M'}).groupby(dividing_dimension).first()['M']
                                    - result_set[result_set['year'] == subspace['year']-1].rename(columns={self.measure:'M'}).groupby(dividing_dimension).first()['M'])
                result_set = result_set.merge(group_delta_prev, on=dividing_dimension)

            # Now, filter by the subspace value of the analysis dimension that
            # we left out of the temp_subspace before
            result_set = result_set[result_set[analysis_dimension] == subspace[analysis_dimension]]

            return result_set[result_set['M'].notnull()]


    def is_valid(self, subspace, dimension, composite_extractor):
        """
        A composite extractor is invalid iff pct is not the first extractor used.
        With a depth of 2 (and only 1 extractor), this is never a concern.

        A sibling group SG(S, Da) is a valid input for composite extractor Ce iff
        for each pair (E, Dx) in Ce, Dx=Da or S[Dx] != "∗" (all values).

        In addition, the extractor delta_prev is only valid for ordinal dimensions;
        Assume that the only ordinal dimension will be 'year'.
        """
        logging.info("is_valid(%s, %s, %s)" % (subspace, dimension, composite_extractor))
        for (extractor, measure) in composite_extractor[1:]:
            if measure != dimension and subspace.get(measure) is None:
                return False

            if extractor == 'delta_prev' and measure != 'year':
                return False

        return True


    def impact(self, subspace, dimension):
        """
        The impact score is the market share of the subspace S.
        """
        logging.info("impact(%s, %s)" % (subspace, dimension))
        subset = self.data.loc[(self.data[list(subspace)] == pd.Series(subspace, dtype=object)).all(axis=1)]

        numerator = subset[self.measure].sum()
        denominator = self.total_measure_sum

        impact_score = float(numerator / denominator)
        assert(0.0 <= impact_score <= 1.0)

        return impact_score



class Insight:

    csv_header = "id;score;type;SG(S,D);CE;insight;H0;sig;impact"

    def __init__(self, id, insight, score, subspace, dimension, composite_extractor,
                 insight_type, significance, sigtest, impact):
        self.id = id
        self.insight = insight
        self.score = score
        self.subspace = subspace
        self.dimension = dimension
        self.composite_extractor = composite_extractor
        self.insight_type = insight_type
        self.significance = significance
        self.sigtest = sigtest
        self.impact = impact

    def __lt__(self, other):
        return self.score < other

    def __gt__(self, other):
        return self.score > other

    def __eq__(self, other):
        return self.score == other.score

    def interpretation(self):
        if len(self.composite_extractor) == 2:
            agg = "{extractor} of {analysis_dimension} of {measure}".format(
                extractor=self.composite_extractor[1][0],
                analysis_dimension=self.composite_extractor[1][1],
                measure=self.composite_extractor[0][0])
        else:
            agg = "{measure}".format(measure=self.composite_extractor[0][0])

        return ("Aggregating {agg} over dividing dimension {dimension}," +
                "{insight} stood out using {sigtest} test, considering only " +
                "the subspace with dimensions {subspace}").format(
                    agg=agg,
                    dimension=self.dimension,
                    insight=self.insight,
                    sigtest=self.sigtest,
                    subspace=self.subspace)

    def to_csv(self):
        return "%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
            self.id,
            round(self.score, 4),
            self.insight_type,
            "SG(%s,%s)" % (self.subspace, self.dimension),
            self.composite_extractor,
            self.insight,
            self.sigtest,
            round(self.significance, 4),
            round(self.impact, 4))


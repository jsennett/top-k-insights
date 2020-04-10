import logging

def extract_insights(dataset, depth, k):
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

    # TODO: maintain a global min-heap that will be updated with top insights
    topk = None

    # Enumerate all composite extractors for depth 1 or 2
    if depth == 1:
        composite_extractors =  [[("sum", dataset.measure)]]
    elif depth == 2:
        composite_extractors = []
        for dimension in dataset.dimensions:
            for extractor in ["rank", "delta_prev", "pct", "delta_avg"]:
                composite_extractors += [[("sum", dataset.measure), (extractor, dimension)]]
    else:
        raise ValueError("Expected depth of 1 or 2, not", depth)
    logging.info("Considering composite extractors:")
    logging.info(composite_extractors)


    for composite_extractor in composite_extractors:
        for dimension in dataset.dimensions:
            enumerate_insight({}, dimension, composite_extractor, dataset)

    # TODO: return the topk insights, format them, etc.
    return topk

def enumerate_insight(subspace, dimension, composite_extractor, dataset):
    """
    if is_valid(subspace, dimension, composite extractor):
        result_set = extract(subspace, dimensionm, composite extractor)
        for each insight type:
            score = impact(subspace, dimension) * significance(result_set)
    """
    if is_valid(subspace, dimension, composite_extractor):
        logging.info("    Valid SG/CE combo: subspace(%s), dim(%s), ce(%s)" % (subspace, dimension, composite_extractor))
        result_set = None # Placeholder; extract result_set by appling CE to SG(S, Dx)
        score = impact(subspace, dimension) * significance(result_set)
        # todo: update min-heap if score exceeds top kth score
    else:
        logging.info("Invalid SG/CE combo: subspace(%s), dim(%s), ce(%s)" % (subspace, dimension, composite_extractor))

    # Enumerate child subspaces
    for value in dataset.data[dimension].unique():
        subspace[dimension] = value
        for new_dimension in set(dataset.dimensions) - set(subspace):
            enumerate_insight(subspace, new_dimension, composite_extractor, dataset)


def is_valid(subspace, dimension, composite_extractor):
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


def impact(subspace, dimension):
    """
    """
    import random
    return random.randint(0,100) / 100 # placeholder


def significance(result_set):
    """
    """
    import random
    return random.randint(0,100) / 100 # placeholder


def main():
    pass



if __name__ == "__main__":
    main()



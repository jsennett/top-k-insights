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


    for extractor in composite_extractors:
        for dimension in dataset.dimensions:
            enumerate_insight({}, dimension, extractor)

    # TODO: return the topk insights, format them, etc.
    return topk

def enumerate_insight(subspace, dimension, composite_extractor):
    """
    if is_valid(subspace, dimension, composite extractor):
        result_set = extract(subspace, dimensionm, composite extractor)
        for each insight type:
            score = impact(subspace, dimension) * significance(result_set)
    """
    if is_valid(subspace, dimension, composite_extractor):
        pass

    else:
        logging.info("Invalid SG/CE pair, skipping.")
        logging.info("Subspace: " + str(subspace))
        logging.info("Dividing Dimension: " + str(dimension))
        logging.info(str(composite_extractor)

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
    pass


def significance(result_set):
    """
    """
    pass


def main():
    pass



if __name__ == "__main__":
    main()



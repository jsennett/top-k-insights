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
    pass

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



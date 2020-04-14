from top_k_insights.dataset import Dataset

dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")

def test_init():
    assert(len(dataset.dimensions) == 3)
    assert(dataset.measure == "vehicles")
    assert(len(dataset.data) == 96)
    assert(len(dataset.data.columns) == 4)

def test_extract_result_set():
    dataset.depth = 2

    # Test each extractor type
    subspace = {"brand":"Toyota"}
    dividing_dimension = "year"
    analysis_dimension = "year"
    for extractor in ['rank', 'pct', 'delta_avg', 'delta_prev']:
        ce = [('sum', 'vehicles'), (extractor, analysis_dimension)]
        assert(dataset.is_valid(subspace, dividing_dimension, ce))

        print("-" * 40)
        print(extractor + " across " + analysis_dimension + "s of sum of sales per " + dividing_dimension + ", just considering the subspace of", subspace)
        results = dataset.extract_result_set(subspace, dividing_dimension, ce)
        print(results)

    # Test different dimensions
    subspace = {}
    dividing_dimension = "country"
    analysis_dimension = "country"
    for extractor in ['rank', 'pct', 'delta_avg']:
        ce = [('sum', 'vehicles'), (extractor, analysis_dimension)]
        assert(dataset.is_valid(subspace, dividing_dimension, ce))

        print("-" * 40)
        print(extractor + " across " + analysis_dimension + "s of sum of sales per " + dividing_dimension + ", just considering the subspace of", subspace)
        results = dataset.extract_result_set(subspace, dividing_dimension, ce)
        print(results)

     # Test where subspace[analysis_dimension] != *
    subspace = {'brand':'Toyota'}
    dividing_dimension = "year"
    analysis_dimension = "brand" # issue: makes no difference if this is year or brand
    for extractor in ['rank', 'pct', 'delta_avg']:
        ce = [('sum', 'vehicles'), (extractor, analysis_dimension)]
        assert(dataset.is_valid(subspace, dividing_dimension, ce))

        print("-" * 40)
        print(extractor + " across " + analysis_dimension + "s of sum of sales per " + dividing_dimension + ", just considering the subspace of", subspace)
        results = dataset.extract_result_set(subspace, dividing_dimension, ce)
        print(results)

    # Example from paper: (delta_prev, year) for each brand and year
    subspace = {"year":2012}
    dividing_dimension = "brand"
    analysis_dimension = "year"
    extractor = 'delta_prev'
    ce = [('sum', 'vehicles'), (extractor, analysis_dimension)]
    print("-" * 40)
    print(extractor + " of " + analysis_dimension + "s of sum of sales per " + dividing_dimension + ", just considering the subspace of", subspace)
    results = dataset.extract_result_set(subspace, dividing_dimension, ce)
    print(results)


def test_extract_insights_depth1():
    dataset.extract_insights(depth=1, k=5)
    print("Top insights:", dataset.top_insights)
    # TODO: some  tests

def test_extract_insights_depth2():
    dataset.extract_insights(depth=2, k=5)
    print("Top insights:", dataset.top_insights)
    # TODO: some tests

def test_is_valid():
    # Valid CE/SG combo, using example from the paper
    subspace = {"brand": "F"}
    dimension = "year"
    ce = [("sum", "sales"), ("pct", "year")]
    assert(dataset.is_valid(subspace, dimension, ce))

    # Valid CE/SG combo, using example from the paper
    subspace = {}
    dimension = "brand"
    ce = [("sum", "sales"), ("pct", "year")]
    assert(dataset.is_valid(subspace, dimension, ce) == False)



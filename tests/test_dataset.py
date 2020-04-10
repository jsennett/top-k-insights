from top_k_insights.dataset import Dataset

dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")

def test_init():
    assert(len(dataset.dimensions) == 3)
    assert(dataset.measure == "vehicles")
    assert(len(dataset.data) == 96)
    assert(len(dataset.data.columns) == 4)

def test_extract_result_set():
    subspace = {"brand":"Toyota"}
    dividing_dimension = "year"
    extractor_type = "RANK"

    results = dataset.extract_result_set(subspace, dividing_dimension, extractor_type)
    assert(len(results) != 0)
    assert(all(results.columns == ["year", "vehicles", "rank", "pct", "delta_avg", "delta_prev"]))

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



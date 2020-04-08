from top_k_insights import extract_insights
from top_k_insights.dataset import Dataset

cars_dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")

def test_extract_insights_depth1():
    extract_insights.extract_insights(cars_dataset, depth=1, k=5)
    # TODO: some  tests

def test_extract_insights_depth2():
    extract_insights.extract_insights(cars_dataset, depth=2, k=5)
    # TODO: some tests

def test_is_valid():
    # Valid CE/SG combo, using example from the paper
    subspace = {"brand": "F"}
    dimension = "year"
    ce = [("sum", "sales"), ("pct", "year")]
    assert(extract_insights.is_valid(subspace, dimension, ce))

    # Valid CE/SG combo, using example from the paper
    subspace = {}
    dimension = "brand"
    ce = [("sum", "sales"), ("pct", "year")]
    assert(extract_insights.is_valid(subspace, dimension, ce) == False)



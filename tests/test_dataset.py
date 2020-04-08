from top_k_insights.dataset import Dataset

def test_dataset():
    cars_dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")
    assert(len(cars_dataset.dimensions) == 3)
    assert(cars_dataset.measure == "vehicles")
    assert(len(cars_dataset.data) == 96)
    assert(len(cars_dataset.data.columns) == 4)

def test_extract():
    cars_dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")
    subspace = {"brand":"Toyota"}
    dividing_dimension = "year"
    extractor_type = "RANK"

    results = cars_dataset.extract(subspace, dividing_dimension, extractor_type)
    assert(len(results) != 0)
    assert(all(results.columns == ["year", "vehicles", "rank", "pct", "delta_avg", "delta_prev"]))

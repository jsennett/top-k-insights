from top_k_insights.dataset import Dataset

def test_dataset():
    cars_dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")
    assert(cars_dataset.dimension_names == ["year", "brand", "country"])
    assert(cars_dataset.measure_name == "vehicles")
    assert(len(cars_dataset.data) == 96)
    assert(len(cars_dataset.data[0]) == 4)




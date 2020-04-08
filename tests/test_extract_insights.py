from top_k_insights.extract_insights import extract_insights
from top_k_insights.dataset import Dataset

cars_dataset = Dataset("/Users/jsennett/Code/top-k-insights/data/vehicle-sales.csv")

def test_extract_insights_depth1():
    extract_insights(cars_dataset, depth=1, k=5)


def test_extract_insights_depth2():
    extract_insights(cars_dataset, depth=2, k=5)

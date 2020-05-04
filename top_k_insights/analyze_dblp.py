from dataset import Dataset
import pandas as pd

import logging
from datetime import datetime
import time

log_filename = datetime.now().strftime('mylogfile_%H_%M_%d_%m_%Y.log')
logging.basicConfig(level=logging.DEBUG, filename='output.log')

def analyze_papers():
    """ Analyze papers dataset """
    filename = "/Users/jsennett/Code/top-k-insights/data/all-papers.csv"
    data = pd.read_csv(filename, encoding='mac_roman', dtype = {'school': str})

    # Exclude venue name
    # dimensions = ['venue_name', 'year', 'school', 'venue_type']
    dimensions = ['year', 'school', 'venue_type']
    measure = None
    agg = 'count'
    dataset = Dataset(data, dimensions, measure, agg)
    del dataset.data['venue_name']
    logging.info("dataset columns: %s " % dataset.data.columns)

    top_insights = dataset.extract_insights(depth=2, k=10)
    print("Top insights:")
    sorted_insights = sorted(top_insights, key=lambda x:x.score)
    for insight in sorted_insights:
        print(insight.interpretation())



def analyze_papers_subset():
    """ Analyze papers dataset """
    filename = "/Users/jsennett/Code/top-k-insights/data/all-papers.csv"
    data = pd.read_csv(filename, encoding='mac_roman', dtype = {'school': str})

    # Use a subset for debugging
    data = data[data.index % 15 == 0]

    # todo: all dimensions
    # dimensions = ['venue_name', 'year', 'school', 'venue_type']
    dimensions = ['venue_name', 'venue_type', 'year']
    measure = None
    agg = 'count'
    dataset = Dataset(data, dimensions, measure, agg)

    logging.info("dataset columns: %s " % dataset.data.columns)

    top_insights = dataset.extract_insights(depth=2, k=15)
    print("Top insights:")
    sorted_insights = sorted(top_insights, key=lambda x:x.score)
    for insight in sorted_insights:
        print(insight.interpretation())

def analyze_papers_single_insight():

    filename = "/Users/jsennett/Code/top-k-insights/data/all-papers.csv"
    data = pd.read_csv(filename, encoding='mac_roman', dtype = {'school': str})

    dimensions = ['mod2', 'venue_type', 'year']
    data['mod2'] = data.index % 2
    measure = None
    agg = 'count'
    dataset = Dataset(data, dimensions, measure, agg)
    logging.info("dataset columns: %s " % dataset.data.columns)

    dataset.top_insights = []
    dataset.k = 10
    dataset.depth = 2
    subspace = {}
    dataset.enumerate_insight(subspace,
                              'year',
                              [['count','count'], ['pct','year']])

def analyze_papers_single_insight_2():

    filename = "/Users/jsennett/Code/top-k-insights/data/all-papers.csv"
    data = pd.read_csv(filename, encoding='mac_roman', dtype = {'school': str})

    dimensions = ['mod2', 'venue_name', 'year']
    data['mod2'] = data.index % 2
    measure = None
    agg = 'count'
    dataset = Dataset(data, dimensions, measure, agg)
    logging.info("dataset columns: %s " % dataset.data.columns)

    dataset.top_insights = []
    dataset.k = 10
    dataset.depth = 2
    subspace = {'year':2000}
    dataset.enumerate_insight(subspace,
                              'venue_name',
                              [['count','count'], ['delta_prev','year']])




def main():
    #analyze_papers()
    analyze_papers_subset()
    #analyze_papers_single_insight()
    #analyze_papers_single_insight_2()


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("*"*40)
    print(" Finished analysis of DBLP in %0.2f seconds" % (end - start))
    print("*"*40)

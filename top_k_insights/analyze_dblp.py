from dataset import InsightExtractor, Insight
import pandas as pd

import logging
from datetime import datetime
import time

# Log to file
log_filename = datetime.now().strftime('log/topk_%m_%d_%H_%M_%S.log')
logging.basicConfig(level=logging.INFO, filename=log_filename)
bar = "*" * 60

def analyze_papers(depth):
    """ Analyze papers dataset """
    filename = "/Users/jsennett/Code/top-k-insights/data/all-papers.csv"

    data = pd.read_csv(filename, encoding='mac_roman', dtype = {'school': str})
    dimensions = ['venue_name', 'year', 'school', 'venue_type']
    measure = None
    agg = 'count'
    dataset = InsightExtractor(data, dimensions, measure, agg)

    top_insights = dataset.extract_insights(depth=depth, k=10)

    print_top_insights(top_insights)

def analyze_paperauths(depth):
    """ Analyze papers dataset """
    filename = "/Users/jsennett/Code/top-k-insights/data/all-paperauths.csv"
    data = pd.read_csv(filename, encoding='mac_roman')

    dimensions = ['paperid', 'authid', "year"]
    measure = None
    agg = 'count'

    dataset = InsightExtractor(data, dimensions, measure, agg)
    logging.info("dataset columns: %s " % dataset.data.columns)

    top_insights = dataset.extract_insights(depth=depth, k=10)
    print_top_insights(top_insights)

def print_top_insights(top_insights):

    sorted_insights = sorted(top_insights, key=lambda x:x.score, reverse=True)

    print(bar)
    print("TOP INSIGHTS: CSV")
    print(bar)

    logging.info(Insight.csv_header)
    print(Insight.csv_header)
    for insight in sorted_insights:
        logging.info(insight.to_csv())
        print(insight.to_csv())

    print(bar)
    print("TOP INSIGHTS: INTERPRETATION")
    print(bar)

    for insight in sorted_insights:
        logging.info(insight.interpretation())
        print(insight.interpretation())


def main():
    # TODO: make this a CLI program
    #analyze_papers(1)
    #analyze_papers(2)
    #analyze_paperauths(1)
    analyze_paperauths(2)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(bar)
    print(" Finished analysis of DBLP in %0.2f seconds" % (end - start))
    print(bar)

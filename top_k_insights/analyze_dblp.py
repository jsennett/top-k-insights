from insight_extractor import InsightExtractor, Insight
import pandas as pd

import logging
from datetime import datetime
import time
import argparse

# Log to file
log_filename = datetime.now().strftime('log/topk_%m_%d_%H_%M_%S.log')
logging.basicConfig(level=logging.INFO, filename=log_filename)
bar = "*" * 60


def main():

    # Parse input args
    parser = argparse.ArgumentParser(description='Extract Top Insights from DBLP')
    parser.add_argument('dataset', type=str, help="'papers' or 'collaborators'")
    parser.add_argument('depth', type=int, help="1 or 2")
    parser.add_argument('k', type=int, help="1 to 100, integer")
    parser.add_argument('-encoding', type=str, help="dataset encoding; ('mac_roman' works on locally)")
    args = parser.parse_args()

    # Validate input args
    if (args.dataset not in ['papers', 'collaborators']
        or args.depth not in [1, 2]
        or args.k < 1
        or args.k > 100):
        parser.print_help()
        parser.print_usage()

    # Check for datasets
    if args.dataset == 'papers':
        filename = "./data/all-papers.csv"
        data = pd.read_csv(filename, encoding=args.encoding, dtype = {'school': str})
        dimensions = ['venue_name', 'year', 'school', 'venue_type']
        measure = None
        agg = 'count'

    if args.dataset == 'collaborators':
        filename = "./data/all-paperauths.csv"
        data = pd.read_csv(filename, encoding=args.encoding, dtype = {'school': str})
        dimensions = ['venue_name', 'year', 'school', 'venue_type']
        measure = None
        agg = 'count'


    ie = InsightExtractor(data, dimensions, measure, agg)
    top_insights = ie.extract_insights(depth=args.depth, k=args.k)
    print_top_insights(top_insights)



if __name__ == "__main__":
    main()






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


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(bar)
    print(" Finished analysis of DBLP in %0.2f seconds" % (end - start))
    print(bar)

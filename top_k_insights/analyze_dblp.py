from dataset import Dataset
import pandas as pd

import logging
from datetime import datetime
import time

# Log to file
log_filename = datetime.now().strftime('top-k-log_%H_%M_%d_%m_%Y.log')
logging.basicConfig(level=logging.DEBUG, filename=log_filename)

def analyze_papers():
    """ Analyze papers dataset """
    filename = "/Users/jsennett/Code/top-k-insights/data/all-papers.csv"
    data = pd.read_csv(filename, encoding='mac_roman', dtype = {'school': str})

    dimensions = ['venue_name', 'year', 'school', 'venue_type']
    measure = None
    agg = 'count'
    dataset = Dataset(data, dimensions, measure, agg)
    logging.info("dataset columns: %s " % dataset.data.columns)

    top_insights = dataset.extract_insights(depth=2, k=100)

    logging.info("Top insights:")
    sorted_insights = sorted(top_insights, key=lambda x:x.score)
    for insight in sorted_insights:
        logging.info(insight.interpretation())
        print(insight.interpretation())

def main():
    analyze_papers()


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("*"*40)
    print(" Finished analysis of DBLP in %0.2f seconds" % (end - start))
    print("*"*40)

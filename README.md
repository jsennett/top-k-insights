# top-k-insights
Reproducing results from "Extracting Top-K Insights from Multidimensional Data"

# Instructions
1) Install dependencies using pip. This project was developed using Python 3.6.1 and only a few common libraries. (You may have to use `pip3` instead of `pip`).
```
pip install --user -r requirements.txt
```

2) Extract insights from the 'papers' or 'collaborators' DBLP dataset. This will print output to the console, and more verbose logs will be created in `./log/`

__Examples__
```sh
# Top-10 depth-2 insights from DBLP papers 
python3 ./top_k_insights/analyze_dblp.py papers 2 10

# Top-10 depth-2 insights from DBLP collaborators 
python3 ./top_k_insights/analyze_dblp.py collaborators 2 10

# Top-10 depth-1 insights from DBLP papers 
python3 ./top_k_insights/analyze_dblp.py papers 1 10

# Top-10 depth-1 insights from DBLP collaborators 
python3 ./top_k_insights/analyze_dblp.py collaborators 1 10
```

# Project Layout

`./top_k_insights/` contains source code for insight extraction

`./top_k_insights/insight_extractor.py` contains the insight extraction engine, including the `InsightExtractor` class

`./top_k_insights/significance_tests.py` contains the point and trend significance functions

`./top_k_insights/analyze_dblp.py` is a command-line program you can use to extract insights from the DBLP dataset

`./tests/` Unit tests of significance functions are tested here, and can be run using the command `pytest`, if pytest is installed.

`./log/` Log files with timestamped filenames will be created here each time `./top_k_insights/analyze_dblp.py` is called.

`./data/` The datasets `all-papers.csv` and `all-paperauths.csv` are expected to be here.

`./report/final-report.pdf` Final Report

`./report/notebooks/` Jupyter Notebooks containing analysis and figures highlighted in the final report.

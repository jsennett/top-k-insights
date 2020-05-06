#!/usr/bin/env bash
mkdir -p submission/top_k_insights/
mkdir -p submission/report/notebooks/
mkdir -p submission/data/
mkdir -p submission/log/
mkdir -p submission/tests/

cp README.md submission/README.md 
cp requirements.txt submission/requirements.txt 
cp top_k_insights/__init__.py submission/top_k_insights/__init__.py 
cp top_k_insights/analyze_dblp.py submission/top_k_insights/analyze_dblp.py 
cp top_k_insights/insight_extractor.py submission/top_k_insights/insight_extractor.py 
cp top_k_insights/significance_tests.py submission/top_k_insights/significance_tests.py 
cp data/papers-query.sql submission/data/papers-query.sql 
cp data/paperauths-query.sql submission/data/paperauths-query.sql 
cp data/all-paperauths.csv submission/data/all-paperauths.csv 
cp data/all-papers.csv submission/data/all-papers.csv 
cp tests/test_sigtests.py submission/tests/test_sigtests.py 
cp report/final-report.pdf submission/report/final-report.pdf 
cp report/notebooks/*.pdf submission/report/notebooks/
cp log/*.log submission/log/

zip -r joshuasennett.zip submission

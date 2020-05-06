import top_k_insights.significance_tests as st
import pandas as pd
import numpy as np
import random

def test_powerlaw():

    # perfect fit powerlaw with guassian noise
    rs = pd.DataFrame([10*(x**-.1) + np.random.normal() for x in range(10, 1000)], columns=['M'])
    (insight, sig) = st.powerlaw(rs)
    print(sig, insight, "expected max:", max(rs['M']))
    assert(sig < 0.01)

    # perfect fit powerlaw with guassian noise but an extreme max value
    rs = pd.DataFrame([10*(x**-.1) + np.random.normal() for x in range(10, 1000)], columns=['M'])
    rs.iloc[-1] += 200
    (insight, sig) = st.powerlaw(rs)
    print(sig, insight, "expected max:", max(rs['M']))
    assert(sig > 0.99)

def test_normal():

    # perfect fit powerlaw with guassian noise but an extreme max value
    rs = pd.DataFrame([10 * np.random.normal() + 15 for _ in range(10000)], columns=['M'])
    rs.iloc[-1] += 15000
    (insight, sig) = st.normal(rs)
    print(insight, "expected max:", max(rs['M']))
    print("significance score:", sig, "(expected: >", .99, ")")
    assert(sig > 0.99)

def test_linear_point():
    # perfect fit linear relation y = 2x with random normal noise
    rs = pd.DataFrame(zip(range(1000), [x + random.random() for x in range(0, 2000, 2)]), columns=["year", "M"])
    rs['err'] = rs['M'] - 2 * rs['year']

    # Make a point really high off
    rs['M'][500] += 10000

    (insight, sig) = st.linear_point(rs)
    print(insight, "expected insight: {%0.2f} at x=%d" % (rs['M'][500], rs['year'][500]))
    print("significance score:", sig, "(expected: >", .9, ")")
    assert(sig > 0.9)

def test_linear_negative_point():
    # perfect fit linear relation y = 2x with random normal noise
    rs = pd.DataFrame(zip(range(1000), [x + random.random() for x in range(0, 2000, 2)]), columns=["year", "M"])
    rs['err'] = rs['M'] - 2 * rs['year']

    # Make a point really low off
    rs['M'][500] -= 10000

    (insight, sig) = st.linear_point(rs)
    print(insight, "expected insight: {%0.2f} at x=%d" % (rs['M'][500], rs['year'][500]))
    print("significance score:", sig, "(expected: >", .9, ")")
    assert(sig > 0.9)

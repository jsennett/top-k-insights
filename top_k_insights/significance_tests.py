import numpy as np
import scipy
import scipy.stats


def get_distribution(insight_type, dimension, depth, composite_extractor):
    """
    This takes the place of the configuration layer, where users would specify
    null hypotheses for their data. Based on reviewing the data, I have found:

    depth 1:
        count of papers over a categorical dimension -> power-law distribution
        count of papers over an ordinal dimension -> linear distribution

    depth 2:
        'pct' over a categorical dimension -> gaussian distribution
        delta_prev -> positive and negative fit two power-law distributions.
                      Properly fitting means cutting off long tails; for now,
                      try to fit the top half of the positive and negative data.

    """
    if insight_type == "shape":
        return linear_shape
    else:

        # TODO: have a separate point estimate for linear trends
        ordinal = (dimension == 'year')
        if depth == 1 and ordinal:
            return linear_point
        elif depth == 1 and not ordinal:
            return powerlaw
        elif depth == 2 and ordinal:
            return linear_point

        # TODO: determine best fit for these composite aggregate measures
        elif depth == 2 and not ordinal and composite_extractor[1][0] == 'pct':
            return normal
        elif depth == 2 and not ordinal and composite_extractor[1][0] == 'delta_prev':
            return normal
        elif depth == 2 and not ordinal and composite_extractor[1][0] == 'delta_avg':
            return normal
        elif depth == 2 and not ordinal and composite_extractor[1][0] == 'rank':
            return normal


def powerlaw(rs):
    """
    input:
        rs: a DataFrame result set with measure column 'M'.
        min_or_max: a string 'min' or 'max', for which
    output:
        (string, float) tuple of insight and significance score

    To fit power law distribution, convert to an equivalent linear model
        powerlaw:           y = ax^b
        equivalent linear:  log(y) = log(a) + b*log(x)

    A maximum value is significant based on the p value of the error between
    the max value and the predicted max value of the best fit powerlaw dist.
    """
    # Sanity checks:
    assert all(rs['M'] > 0), "powerlaw is only valid for positive distributions"

    # x_max
    x_max = rs['M'].max()
    x_max_idx = rs['M'].idxmax()

    # X \ x_max
    rs = rs.drop(x_max_idx)

    # X, Y are rank and value of 'M'
    rs['logy'] = np.lib.scimath.log2(rs['M'])
    rs['logx'] = np.lib.scimath.log2(rs['M'].rank(method='first', ascending=False))

    # Fit power law distribution by fitting linear model to log
    slope, intercept, r, p, stderr = scipy.stats.linregress(rs['logx'], rs['logy'])

    # Calculate errors
    rs['err'] = 2**(intercept + slope * rs['logx']) - rs['M']

    # x_max_err is the difference between expected x_max (rank=1)
    # and actual x_max.  The predicted value is:
    # _y = 2**(log(a) + b*log(1)) = 2**(loga) = a = 2**intercept
    x_max_err = 2**(intercept) - x_max

    # Fit to Guassian distribution
    # An extreme value means that x_max exceeded the predicted x_max
    # This would result in a negative x_max_err, so only do a one-sided test
    Z = (x_max_err - rs['err'].mean())/rs['err'].std()
    significance_score = 1 - scipy.stats.norm.cdf(Z)

    insight = "maximum point %0.2f" % x_max

    return (insight, significance_score)



def normal(rs):
    """
    input:
        rs: a DataFrame result set with measure column 'M'.
        min_or_max: a string 'min' or 'max', for which
    output:
        (string, float) tuple of insight and significance score

    A maximum or minimum value is significant based on its p value from the
    best fit normal distribution versus the p value expected from the nth
    data point (which would have a p value of 1/n).

    The significance is defined as max(1 - pval(x_max) / alpha, 0),
    where alpha is the expected p value (1/n).

    if pval(x_max)/alpha > 1, the point is certainly not significant;
    so, report a significance of 0.
    """
    # x_max
    x_max = rs['M'].max()
    x_len = len(rs)

    # Fit normal distribution
    x_mean = rs['M'].mean()
    x_std = rs['M'].std()

    # Calculate significance
    x_max_Z = (x_max - x_mean) / x_std
    x_max_p = 1 - scipy.stats.norm.cdf(x_max_Z)
    alpha = 1 / x_len
    significance_score = max(1 - x_max_p / alpha, 0.0)
    insight = "maximum point %0.2f" % x_max

    return (insight, significance_score)


def linear_shape(rs):
    """
    input: rs is a result set dataframe with measure column 'M',
    output: a tuple (string, float) of the insight found to be significant,
            and the p value indicating how significant the insight is.

    Calculating the shape_significance is only relevant when
    the dividing dimension is ordinal. For example, when the
    sibling group uses "year" as its dividing dimension.
    """
    assert("year" in rs.columns and "M" in rs.columns)
    slope, intercept, r, p, stderr = scipy.stats.linregress(rs['year'], rs['M'])

    # Interpret results
    if slope > 0:
        insight = "positive slope %0.2f" % slope
    else:
        insight = "negative slope %0.2f" % slope

    return (insight, (r**2) * (1 - p))


def linear_point(rs):
    """
    input: rs is a result set dataframe with measure column 'M',
    output: a tuple (string, float) of the insight found to be significant,
            and the p value indicating how significant the insight is.
    """
    assert("year" in rs.columns and "M" in rs.columns)
    slope, intercept, r, p, stderr = scipy.stats.linregress(rs['year'], rs['M'])

    # err = y - pred_y
    rs['err'] = rs['M'] - intercept + slope * rs['year']

    # Fit errors to normal distribution, and see how far off the furthest error is
    x_mean, x_std = scipy.stats.norm.fit(rs['err'])
    max_err_idx = rs['err'].abs().idxmax()
    max_err = rs['err'][max_err_idx]
    err_rs = rs[['err']].rename(columns={'err':'M'})

    # If we're considering a negative err, flip the sign since normal
    # sig test looks for maximum values
    negative_error = (max_err < 0)
    if negative_error:
        _, err_significance = normal(-err_rs)
    else:
        _, err_significance = normal(err_rs)

    # Weight the significance score by the goodness of fit
    # of the line excluding the maximum error point
    _, _, r, _, _ = scipy.stats.linregress(rs['year'].drop(max_err_idx), rs['M'].drop(max_err_idx))

    significance_score = err_significance * (r**2)

    # A positive err means the actual value > predicted value
    if negative_error:
        insight = "year {%d} surprisingly low at {%0.2f}" % (rs['year'][max_err_idx], rs['M'][max_err_idx])
    else:
        insight = "year {%d} surprisingly high at {%0.2f}" % (rs['year'][max_err_idx], rs['M'][max_err_idx])

    return insight, significance_score



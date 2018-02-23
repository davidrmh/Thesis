# Pattern recognition through perceptually important points in financial time series-*G. Zaib, U. Ahmed & A. Ali*.

**Perceptually important points (PIP)** They represent the minimal set of data points which are necessary to form a pattern.

To find a PIP the time series is divided into segments and then each segment is explored in order to find the patterns. This segmentation is based on the maximum and minimum values a time series can take.

**Advantages of using PIP**
* Time unit independence. Good property for dealing with both low and high frequency data.

* No need for smoothing.

* No need to filling for missing data, we are just interested in the PIP.

## PIP identification algorithm

1. Find the minimum and maximum value of the time series.

2. Horizontally divide the whole time series into segments using a *segmentation factor*.

3. Start PIP identification process starting with the most dense segment.

4. Find neighboring PIPs.

5. The pattern is successfully identified if the number of PIPs found is the same as the specified number of points in the pattern.

## Observations

* Paper has bad redaction which makes the reading complicated and confusing (for read the description of pattern description language  for figure figure 7).

* Patter definition language seems a good idea, unfortunately is not well documented.

* No trading strategies designed and no real data experiments.

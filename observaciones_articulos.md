# **Using genetic algorithms to find technical trading rules** - Franklin Allen, Risto Karjalainen (1999)

* Genetic programming approach.
* Contains a brief review of how genetic programming algorithms work.
* Daily closing data from S&P 500.
* Considers *one-way* transaction costs of 0.25%, 0.1% and 0.5%.
* Don't beat *buy-hold* strategy when considering transaction costs.
* No short-sales.
* Split the days in two categories *in the market (earning the market return)* and *out of market (earning the risk free rate)* this implies Buy/sell signals.
* The trading strategy specifies the position to be taken the following day given the current position and the trading rule signal.
* The **function set** includes two kinds of functions: real and boolean.
  + **Real valued functions**
    * *Average(time-series,time-window)* Calculates a moving average.
    * *Maximum/minimum(time-series,time-window)* Calculates the maximum/minimum value of a time series within a time window.
    * *price(time-series)* Returns the closing price of the current day.
    * *norm(val1,val2)* absolute value of the difference between two real numbers.
    * *lag(time-series,time-window)* lags a time series by a number of periods specified in the time window.
  + **Boolean valued functions**
    * *if-then-else*.
    * *and*.
    * *or*.
    * *not*.
    * *>* and *<*.
    * *true*, *false* constants.
 * **Overfitting** is considered by introducing a *selection period* right after the *training-period*. The fittest individual from the current generation is tested on this *selection-period*, if the strategy has higher excess return (fitness) than the best rule so far, the new rule is saved.    

### Fitness function
The fitness function is based on the excess return over the buy-and-hold strategy.
#### Derivation
The **simple return** from a single trade (buy at date $b$ and sell at $s$) is given by

$$\pi = \dfrac{P_{s}}{P_{b}} \times \dfrac{1-c}{1+c} -1 = exp\left[\sum_{t=b+1}^{s} r_{t} + log \dfrac{1-c}{1+1}\right]-1$$

where $P_{t}$ is the closing price on day $t$, $r_{t}=log P_{t} - log P_{t-1}$ is the daily **continuously compounded** return and $c$ is the **one-way** transaction cost (expressed as a fraction of the price).

The return $\pi = \dfrac{\left(P_{s}-P_{b}\right) - c \left(P_{b} + P_{s}\right)}{P_{b}\left(1+c\right)}$ can be obtained as follows:
* On day $b$ buy the asset at price $P_{b}$ and pay a commission of $c P_{b}$  for a total investment of $P_{b}(1+c)$.
* On day $s$ sell the asset at price $P_{s}$ paying a commission of $c P_{s}$.
* The total **simple return** from these two operations is $\dfrac{\left(P_{s}-P_{b}\right) - c \left(P_{b} + P_{s}\right)}{P_{b}\left(1+c\right)}$

Let $T$ be the number of trading days, $r_{f}(t)$ the risk free rate for day $t$,   $\mathbb{I}_{b}(t)$ and $\mathbb{I}_{s}(t)$ the indicator functions for the buy and sell signals at time $t$, respectively; and $n$ the total number of trades, then the **continuously compounded return** for the trading rule is:

$$ r = \sum_{t=1}^{T} r_{t}\mathbb{I}_{b}(t) + \sum_{t=1}^{T}r_{f}(t)\mathbb{I}_{s}(t) + n\times log\dfrac{1-c}{1+c}$$

Whereas the **continuously compounded return** for the *buy-and-hold* strategy (buy on the first day, sell the last day) is:

$$r_{bh}=log(1+\pi)=\sum_{t=1}^{T}r_{t} + log \dfrac{1-c}{1+c}$$

Finally the fitness function is calculated as the excess return over the *buy-and-hold* strategy.

$$\Delta r = r - r_{bh}$$

### Algorithm
* Population size = 500

* Maximum of 100 nodes and 10 levels.

* 50 generations.
~~~
1. Create randomly a population
with 500 individuals
and compute the fitness
for each one of them.

2. Apply the fittest rule in the
selection period.

3. Replace generation using
crossover. Calculate fitness
in the training period.

4. Apply the fittest rule in
the selection period and compute
its fitness, if it improves
upon the previous best rules,
save as the new best rule.
If no improvement for 25
generations or after a total of
50 generations, stop.
Otherwise, go to step 3.
~~~



### Observations
* Only use moving averages and max/min, I think it's a small number of indicators. Can we beat *buy-and-hold* strategy by increasing the number of technical indicators used?

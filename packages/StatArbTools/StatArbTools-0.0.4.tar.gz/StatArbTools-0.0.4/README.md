# StatArbTools

StatArbTools is a Python library primarily for determining if a pair of time series are cointegrated.
It also includes tools for generating an array of log returns from a price array, looking for a linear relationship,
and creating a potentially stationary distribution.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install StatArbTools

```bash
pip install StatArbTools
```

You must also have numpy, scikitlearn, statsmodels, and matplot lib installed

```bash
pip install numpy
```

```bash
pip install sklearn
```

```bash
pip install statsmodels
```

```bash
pip install matplotlib
```

## Usage

```python
import StatArbTools

StatArbTools.gen_log_returns(numpy_time_series_1, numpy_time_series_2) # returns numpy arrays of the log returns for each time series
StatArbTools.gen_linear_relationship(numpy_log_returns_1, numpy_log_returns_2) # returns the coefficient from a linear regression between the two log returns arrays
StatArbTools.gen_stationary_distr(numpy_log_returns_1, numpy_log_returns_2, coefficient) # returns the linear combination of the two log returns arrays based on a linear regression coefficient
StatArbTools.test_stationarity(numpy_time_series_1, numpy_time_series_2) # returns "Rejected null hypothesis" if the null hypothesis of an Augmented Dickey Fuller test is rejected and "Failed to reject" otherwise. It also returns the p-value of the ADF test.
StatArbTools.find_pairs(ticker_data_dict) # returns a list of lists of the results of StatArbTools.test_stationarity for every possible pair of tickers in the dictionary
StatArbTools.portfolio_builder(ticker_data_dict, results) # returns a list of lists of every pair that passed the Augmented Dickey Fuller test and the profitability rating of the pair
StatArbTools.profitability_rating(stationary_distr) # returns a general metric of how profitable a pairs trade would be (note: this is not in dollars, just a means of ranking based on volatility)
StatArbTools.plot(stationary_distribution) # plots the passed distribution
```

**gen_log_returns** takes a numpy array of a time series as a parameter and returns a numpy array of the natural log of the price returns

**gen_linear_relationship** takes two numpy arrays of time series as parameters and returns the coefficient of the least squares regression between the two.
For the statistical arbitrage use case this is used on the log returns of the two stocks to allow for stationarity testing

**gen_stationary_distr** takes two time series and the coefficient of a linear regression between the two (time series must be entered in same order as they were into the linear regression)
and returns the linear combination of the time series that would potentially result in a stationary distribution if the two were cointegrated

**test_stationarity** takes two time series as parameters, constructs log return arrays, determines the linear relationship, constructs a potentially stationary distribution,
and then uses an Augmented Dickey Fuller test at the 1% significane level to check if the distribution is indeed stationary. If it is it will return "Rejected null hypothesis" and the p-value of the test.
If it does not pass the 1% threshold it will return "Failed to reject" and the p-value.

**find_pairs** takes a dictionary with tickers (ie 'aapl', 'adsk', etc) as the keys and a numpy time series array of each ticker's raw prices as the values.
It then constructs every possible pairing of tickers and tests them for cointegration using **test_stationarity**
It will then return an list of lists where each list contains the ticker pair, the null hypothesis result, and the p-value of the test for each pair.

**portfolio_builder** takes a dictionary with tickers(ie 'aapl', 'adsk', etc) as the keys and a numpy time series array of each ticker's raw prices as the values.
It also takes the results array from the **find_pairs** method. It then looks at every pair that rejected the null hypothesis, puts the stationary distribution that results
from them through **profitability_rating** to get a metric to rank based off of. It then constructs a list of lists with the pairs and their ratings and returns
that list of lists sorted by the rating

**profitability_rating** takes a stationary distribution numpy array as an argument, computes the mean and standard deviation of the array and establishes bounds for a 95%
confidence interval around the mean. It then constructs a list with each price in the time series in which the price surpasses this confidence interval. It then returns
the mean of those prices multiplied by the number of those prices. It is not an absolute measure of money made but it gives a method of ranking pairs.

**plot** takes a time series and does a simple matplotlib.pyplot plot. This is primarily useful for visualizing the stationarity of a distribution.

## Contributing
For changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
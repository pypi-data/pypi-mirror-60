import numpy as np
from itertools import combinations
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

#currently unused. may be implemented in the future
'''def __gen_data_list(ticker_list, file_path):
    ticker_data_dict = {}
    for ticker in ticker_list:
        ticker_data_dict.update({ticker : np.genfromtxt(file_path + ticker + '.csv', delimiter=',', skip_header=1)})
    
    return ticker_data_dict
'''
 
def gen_log_returns(time_series):
    
        np_time_series_returns = np.empty(0)
        for index in range(len(time_series) - 1):
            np_time_series_returns = np.append(np_time_series_returns, (time_series[index + 1] - time_series[index]))
               
        return np_time_series_returns
    
    '''if isinstance(time_series, np.ndarray):
        try float(time_series[0]):
            continue
        except ValueError:
            time_series = np.delete(time_series, 1)
        np_time_series_returns = np.empty(0)
        for index in range(len(time_series) - 1):
            np_time_series_returns = np.append(np_time_series_returns, (time_series[index + 1] - time_series[index]))
               
        return np_time_series_returns
    elif isinstance(time_series, pd.core.frame.DataFrame):
        pd_time_series_returns = pd.DataFrame()
        for index in range(len(time_series) - 1):
            pd_time_series_returns = pd_time_series_returns.append(pd.DataFrame(time_series.iloc[index + 1, 0] - time_series[index, 0]))'''
        
def gen_linear_relationship(np_time_series_1_returns, np_time_series_2_returns):
    classifier = LinearRegression(n_jobs = -1)
    classifier.fit(np_time_series_1_returns.reshape(-1,1), np_time_series_2_returns.reshape(-1,1))
        
    return classifier.coef_
    
def gen_stationary_distr(np_time_series_1_returns, np_time_series_2_returns, coefficient):
    stationary_distr = np_time_series_2_returns - (coefficient * np_time_series_1_returns)        
    return stationary_distr
    
def test_stationarity(np_time_series_1, np_time_series_2):
    np_time_series_1_returns = gen_log_returns(np_time_series_1)
    np_time_series_2_returns = gen_log_returns(np_time_series_2)
    coefficient = gen_linear_relationship(np_time_series_1_returns, np_time_series_2_returns)
    stationary_distr = gen_stationary_distr(np_time_series_1_returns, np_time_series_2_returns, coefficient)
        

    adf_result = adfuller(stationary_distr[0])
    if adf_result[1] < 0.01:
        null_hyp = "Rejected null hypothesis"
        return null_hyp, adf_result[1]
    else:
        null_hyp = "Failed to Reject"
        return null_hyp, adf_result[1]
    
def find_pairs(ticker_data_dict):
    ticker_pair_list = combinations(ticker_data_dict, 2)

    results = []
    try:
        for pair in ticker_pair_list:
            time_series_1 = ticker_data_dict[pair[0]]
            time_series_2 = ticker_data_dict[pair[1]]
            
            null_hyp, p_val = test_stationarity(time_series_1, time_series_2)
            pair_results = [pair, null_hyp, p_val]
            results.append(pair_results)
    except IndexError:
        raise Exception("Index Error. Make sure you passed a dictionary with tickers as keys and time series as values")
    
    return results

def portfolio_builder(ticker_data_dict, results):
    portfolio = []
    
    for pair_result in results:
        if pair_result[1] == "Rejected null hypothesis":
            
            time_series_1 = gen_log_returns(ticker_data_dict[pair_result[0][0]])
            time_series_2 = gen_log_returns(ticker_data_dict[pair_result[0][1]])
            coefficient = gen_linear_relationship(time_series_1, time_series_2)
            
            stationary_distr = gen_stationary_distr(time_series_1, time_series_2, coefficient[0][0])
            
            rating = profitability_rating(stationary_distr)
            pair_data = [pair_result[0], rating]
            portfolio.append(pair_data)
    
    portfolio.sort(key=lambda x: x[1])
    return portfolio

#not yet implemented, waiting to also implement Kalman Filter
'''def moving_avg(stationary_distr, gain_factor = 1, mean_estimate = 0):
    updated_mean_estimate = mean_estimate + (1 / gain_factor) * (stationary_distr[-1 * gain_factor] - mean_estimate)
    error_squared = (updated_mean_estimate - mean_estimate)**2
    if gain_factor > 2 and error_squared <= 0.5:
        return updated_mean_estimate
    else:
        gain_factor += 1
        return moving_avg(stationary_distr, gain_factor, updated_mean_estimate)
'''
        
def profitability_rating(stationary_distr):
    mean = np.mean(stationary_distr)
    stdev = np.std(stationary_distr)
    theoretical_trades = []
    trade_count = 0
    noise_filter_upper = mean + 1.96 * stdev
    noise_filter_lower = mean - 1.96*stdev
    
    for tick in stationary_distr:
        if tick >= noise_filter_upper or tick <= noise_filter_lower:
            theoretical_trades.append(tick)
            trade_count += 1
    
    return np.mean(theoretical_trades) * trade_count
    

def plot(stationary_distr):
    plt.plot(stationary_distr[0])
    plt.xlabel("Time")
    plt.ylabel("Diff in Log Returns")
    plt.show()
    
    

    

        

    

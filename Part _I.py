import pandas as pd
import numpy as np
from yahoofinancials import YahooFinancials

def get_ticker_prices(tickers: list, start_date: str, end_date: str, time_interval: str='Daily') -> pd.DataFrame: 
    """
    Gets adjusted closing prices of the given tickers from Yahoo Finance and stores it in a DataFrame.
    
    Args:
        tickers: list of tickers.
        start_date: string 'YYYY-MM-DD'.
        end_date: string 'YYYY-MM-DD'.
        time_interval: string 'Daily' or 'Monthly'.
    
    Returns:
        prices: DataFrame of the adjusted closing prices of the given tickers.
    """

    prices = pd.DataFrame()
    
    for ticker in tickers:
        yf = YahooFinancials(ticker)
        data = yf.get_historical_price_data(start_date=start_date, end_date=end_date, time_interval=time_interval)
        
        # save only the date and adjusted closing price from the returned data
        data = pd.DataFrame(data[ticker]['prices'])[['formatted_date', 'adjclose']]
        # name the column with the ticker
        data.rename({'adjclose': ticker}, axis=1, inplace=True)
        # convert to datetime to enable resampling
        data['formatted_date'] = pd.to_datetime(data['formatted_date'], format="%Y-%m-%d")
        data.set_index('formatted_date', inplace=True)
        data.dropna(inplace=True)
        
        if prices.empty:
            # for the first ticker, set the prices dataframe to the data dataframe
            prices = data.copy()
        else:
            # for subsequent tickers, outer merge on index
            prices = pd.merge(prices, data, left_index=True, right_index=True, how='outer')
        
    return prices

def calc_monthly_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Calulates monthly returns from given prices.
    
    Args:
        prices: DataFrame with daily or monthly price data, one column per asset, datetime index.
    
    Returns:
        returns: DataFrame of monthly returns.
    """
    returns = prices.resample('M').ffill().pct_change().dropna()
    
    return returns

def gerber_cor_cov(returns: pd.DataFrame, threshold_value: float=0.5) -> tuple:
    """
    Computes the Gerber correlation and covariance matrix for a given set of returns.
    
    Args:
        returns: DataFrame of returns, one column per asset, time-based index.
        threshold_value: float to scale standard deviation to determine thresholds.

    Returns:
        cor: DataFrame of the Gerber correlation matrix.
        cov: DataFrame of the Gerber covariance matrix.
    """
    
    # notation from paper
    r = returns
    c = threshold_value
    s = returns.std(axis=0)
    T, K = returns.shape
    
    cov = np.zeros((K, K))
    cor = np.zeros((K, K))
    
    for i in range(K):
        for j in range(i + 1):
            UU_DD = 0
            UD_DU = 0
            NN = 0
            
            # calculate joint observations (with neutrals to ensure PSD)
            for t in range(T):
                rti = r.iloc[t, i]
                rtj = r.iloc[t, j]
                Hi = c * s[i]
                Hj = c * s[j]
                
                # joint observation +1 when series simultaneously pierce their thresholds in same direction
                if (rti >= Hi and rtj >= Hj) or (rti <= -Hi and rtj <= -Hj):
                    UU_DD += 1
                # joint observation -1 when series simultaneously pierce their thresholds in opposite direction
                elif (rti >= Hi and rtj <= -Hj) or (rti <= -Hi and rtj >= Hj):
                    UD_DU -= 1
                # joint observation 0 when series simultanteously don't pierce their thresholds in either direction
                elif rti < Hi and rti > -Hi and rtj < Hj and rtj > -Hj:
                    NN -= 1
                
            # calculate Gerber statistic and place into correlation matrix and copy to lower matrix
            cor[i, j] = (UU_DD + UD_DU) / (T + NN)
            cor[j, i] = cor[i, j]
            
            # calculate Gerber covariance and copy to lower matrix
            cov[i, j] = cor[i, j] * s[i] * s[j]
            cov[j, i] = cov[i, j]
            
    return cor, cov


if __name__ == "__main__":
    # iShares ETFs of the indexes: ['SPX', 'RTY', 'MXEA', 'MXEF', 'LBUSTRUU', 'LF98TRUU', 'FNERTR', 'XAU', 'SPGSCI']
    tickers = ['SPY', 'IWM', 'EFA', 'EEM', 'AGG', 'HYG', 'IYR', 'IAU', 'GSG']
    # earliest date that Yahoo returns price data for all 9 indexes
    start_date = '2007-04-30'
    end_date = '2022-12-31'

    df_prices = get_ticker_prices(tickers, start_date, end_date)
    print(df_prices)
  
    df_monthly_returns = calc_monthly_returns(df_prices)
    print(df_monthly_returns)
  
    tuple_gerber = gerber_cor_cov(df_monthly_returns)

    print(tuple_gerber[0]) # Gerber correlation
    print(tuple_gerber[1]) # Gerber covariance

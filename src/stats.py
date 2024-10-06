import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df.set_index('Date')

def calculate_returns(df):
    return df.pct_change().dropna()

def calculate_beta(returns, market_returns):
    covariance = np.cov(returns, market_returns)[0][1]
    market_variance = np.var(market_returns)
    return covariance / market_variance

def calculate_volatility(returns):
    return returns.std() * np.sqrt(252)  # Annualized volatility

def calculate_max_drawdown(returns):
    cumulative_returns = (1 + returns).cumprod()
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    return drawdown.min()

def calculate_annualized_return(returns):
    return (1 + returns.mean()) ** 252 - 1

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def plot_cumulative_returns(returns, title, output_dir):
    cumulative_returns = (1 + returns).cumprod()
    plt.figure(figsize=(12, 6))
    for col in cumulative_returns.columns:
        plt.semilogy(cumulative_returns.index, cumulative_returns[col], label=col)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns (log scale)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cumulative_returns_log.png'))
    plt.close()

def plot_rolling_beta(returns, market_returns, window=90, output_dir=None):
    rolling_covariance = returns.rolling(window=window).cov(market_returns)
    rolling_market_variance = market_returns.rolling(window=window).var()
    rolling_beta = rolling_covariance / rolling_market_variance

    plt.figure(figsize=(12, 6))
    for col in rolling_beta.columns:
        plt.plot(rolling_beta.index, rolling_beta[col], label=col)
    plt.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    plt.title(f'{window}-Day Rolling Beta')
    plt.xlabel('Date')
    plt.ylabel('Beta')
    plt.legend()
    plt.ylim(-2, 6)  # Adjusted y-axis limits
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rolling_beta.png'))
    plt.close()

def plot_rolling_volatility(returns, window=90, output_dir=None):
    rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
    plt.figure(figsize=(12, 6))
    for col in rolling_vol.columns:
        plt.plot(rolling_vol.index, rolling_vol[col], label=col)
    plt.title(f'{window}-Day Rolling Volatility (Annualized)')
    plt.xlabel('Date')
    plt.ylabel('Volatility')
    plt.legend()
    plt.ylim(0, 2)  # Adjusted y-axis limits
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rolling_volatility.png'))
    plt.close()

def plot_rolling_correlation(returns, window=90, output_dir=None):
    plt.figure(figsize=(12, 6))
    for i in range(len(returns.columns)):
        for j in range(i+1, len(returns.columns)):
            asset1 = returns.columns[i]
            asset2 = returns.columns[j]
            corr = returns[asset1].rolling(window=window).corr(returns[asset2])
            plt.plot(corr.index, corr, label=f'{asset1} vs {asset2}')
    plt.title(f'{window}-Day Rolling Correlation')
    plt.xlabel('Date')
    plt.ylabel('Correlation')
    plt.legend()
    plt.ylim(-1, 1)  # Full correlation range
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rolling_correlation.png'))
    plt.close()

def plot_rolling_sharpe_ratio(returns, risk_free_rate=0.02, window=90, output_dir=None):
    excess_returns = returns - risk_free_rate / 252
    rolling_mean = excess_returns.rolling(window=window).mean()
    rolling_std = excess_returns.rolling(window=window).std()
    rolling_sharpe = np.sqrt(252) * rolling_mean / rolling_std

    plt.figure(figsize=(12, 6))
    for col in rolling_sharpe.columns:
        plt.plot(rolling_sharpe.index, rolling_sharpe[col], label=col)
    plt.title(f'{window}-Day Rolling Sharpe Ratio')
    plt.xlabel('Date')
    plt.ylabel('Sharpe Ratio')
    plt.legend()
    plt.ylim(-2, 6)  # Adjusted y-axis limits
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rolling_sharpe_ratio.png'))
    plt.close()

def plot_rolling_beta(returns, market_returns, window=90, output_dir=None):
    asset_cols = [col for col in returns.columns if col != 'SP500']
    rolling_betas = pd.DataFrame(index=returns.index)
    
    for col in asset_cols:
        rolling_covariance = returns[col].rolling(window=window).cov(market_returns)
        rolling_market_variance = market_returns.rolling(window=window).var()
        rolling_betas[col] = rolling_covariance / rolling_market_variance

    plt.figure(figsize=(12, 6))
    for col in rolling_betas.columns:
        plt.plot(rolling_betas.index, rolling_betas[col], label=col)
    plt.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='β = 1')
    plt.title(f'{window}-Day Rolling Beta (vs S&P 500)')
    plt.xlabel('Date')
    plt.ylabel('Beta')
    plt.legend()
    plt.ylim(-2, 6)  # Adjusted y-axis limits
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rolling_beta.png'))
    plt.close()
    
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, '..', 'output')
    output_dir = os.path.join(script_dir, '..', 'output', 'analysis')
    
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    df = load_data(os.path.join(input_dir, 'mstr_btc_metrics_daily.csv'))
    
    # Select relevant columns and rename
    data = df[['MSTR_Close', 'BTC-USD_Close']].rename(columns={
        'MSTR_Close': 'MSTR',
        'BTC-USD_Close': 'BTC'
    })
    
    # Add S&P 500 data
    sp500 = pd.read_csv(os.path.join(input_dir, 'sp500_data.csv'), index_col='Date', parse_dates=True)
    data['SP500'] = sp500['Close']
    
    # Calculate returns
    returns = calculate_returns(data)
    
    # Generate plots
    plot_cumulative_returns(returns, 'Cumulative Returns: MSTR, BTC, and S&P 500 (Log Scale)', output_dir)
    plot_rolling_beta(returns, returns['SP500'], output_dir=output_dir)
    plot_rolling_volatility(returns, output_dir=output_dir)
    plot_rolling_correlation(returns, output_dir=output_dir)
    plot_rolling_sharpe_ratio(returns, output_dir=output_dir)
    
    print("Statistical analysis complete. Results and plots saved in the 'output/analysis' directory.")

if __name__ == "__main__":
    main()
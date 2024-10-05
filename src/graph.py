import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def plot_btc_holdings_vs_market_cap(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['BTC_Holdings_Value_USD'], label='BTC Holdings Value')
    plt.plot(df['Date'], df['MSTR_Market_Cap_USD'], label='MSTR Market Cap')
    plt.title('MicroStrategy: BTC Holdings Value vs Market Capitalization')
    plt.xlabel('Date')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plot_btc_to_market_cap_ratio(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['BTC_to_Market_Cap_Ratio'])
    plt.title('MicroStrategy: BTC Holdings Value to Market Cap Ratio')
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plot_btc_holdings_vs_market_cap_scatter(df):
    plt.figure(figsize=(12, 8))
    years = df['Year'].unique()
    colors = plt.cm.rainbow(np.linspace(0, 1, len(years)))
    
    for year, color in zip(years, colors):
        year_data = df[df['Year'] == year]
        plt.scatter(year_data['BTC_Holdings_Value_USD'], year_data['MSTR_Market_Cap_USD'], 
                    c=[color], label=str(year), alpha=0.6)
    
    max_value = max(df['BTC_Holdings_Value_USD'].max(), df['MSTR_Market_Cap_USD'].max())
    plt.plot([0, max_value], [0, max_value], 'k--', alpha=0.5, label='1:1 Line')
    
    plt.title('MicroStrategy: BTC Holdings Value vs Market Cap (Scatter)')
    plt.xlabel('BTC Holdings Value (USD)')
    plt.ylabel('MSTR Market Cap (USD)')
    plt.legend(title='Year')
    plt.tight_layout()
    return plt

def plot_financial_leverage_ratio(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Financial_Leverage_Ratio'])
    plt.title('MicroStrategy: Financial Leverage Ratio')
    plt.xlabel('Date')
    plt.ylabel('Leverage Ratio')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plot_btc_to_net_assets_ratio(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['BTC_to_Net_Assets_Ratio'])
    plt.title('MicroStrategy: BTC Holdings Value to Net Assets Ratio')
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def save_plot(plt, filename):
    plt.savefig(filename)
    print(f"Plot saved to {filename}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, '..', 'output')
    output_dir = os.path.join(script_dir, '..', 'output', 'plots')
    
    os.makedirs(output_dir, exist_ok=True)

    daily_data_path = os.path.join(input_dir, 'mstr_btc_metrics_daily.csv')
    df = load_data(daily_data_path)

    plots = [
        (plot_btc_holdings_vs_market_cap, 'btc_holdings_vs_market_cap.png'),
        (plot_btc_to_market_cap_ratio, 'btc_to_market_cap_ratio.png'),
        (plot_btc_holdings_vs_market_cap_scatter, 'btc_holdings_vs_market_cap_scatter.png'),
        (plot_financial_leverage_ratio, 'financial_leverage_ratio.png'),
        (plot_btc_to_net_assets_ratio, 'btc_to_net_assets_ratio.png')
    ]

    for plot_func, filename in plots:
        plt = plot_func(df)
        save_plot(plt, os.path.join(output_dir, filename))
        plt.close()

if __name__ == "__main__":
    main()
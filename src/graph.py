import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import yfinance as yf
import numpy as np

def load_mstr_btc_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def get_mstr_shares_outstanding():
    mstr = yf.Ticker("MSTR")
    return mstr.info['sharesOutstanding']

def calculate_mstr_btc_metrics(df, mstr_shares):
    df['BTC_Holdings_Value_USD'] = df['Total_BTC'] * df['BTC-USD_Close']
    df['MSTR_Market_Cap_USD'] = df['MSTR_Close'] * mstr_shares
    df['BTC_to_Market_Cap_Ratio'] = df['BTC_Holdings_Value_USD'] / df['MSTR_Market_Cap_USD']
    df['Year'] = df['Date'].dt.year
    
    # Calculate financial leverage
    df['Financial_Leverage_Ratio'] = df['Total_Liabilities'] / df['Total_Assets']
    
    # Calculate net assets
    df['Net_Assets_USD'] = df['Total_Assets'] - df['Total_Liabilities']
    
    # Calculate BTC to Net Assets ratio
    df['BTC_to_Net_Assets_Ratio'] = df['BTC_Holdings_Value_USD'] / df['Net_Assets_USD']
    
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
    
    # Add y=x dashed line
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
    data_path = os.path.join(script_dir, '..', 'data', 'mstr_btc_data.csv')
    output_dir = os.path.join(script_dir, '..', 'output')
    
    os.makedirs(output_dir, exist_ok=True)

    df = load_mstr_btc_data(data_path)
    mstr_shares = get_mstr_shares_outstanding()
    df = calculate_mstr_btc_metrics(df, mstr_shares)

    btc_vs_market_cap_plot = plot_btc_holdings_vs_market_cap(df)
    save_plot(btc_vs_market_cap_plot, os.path.join(output_dir, 'btc_holdings_vs_market_cap.png'))

    btc_to_market_cap_ratio_plot = plot_btc_to_market_cap_ratio(df)
    save_plot(btc_to_market_cap_ratio_plot, os.path.join(output_dir, 'btc_to_market_cap_ratio.png'))

    btc_vs_market_cap_scatter_plot = plot_btc_holdings_vs_market_cap_scatter(df)
    save_plot(btc_vs_market_cap_scatter_plot, os.path.join(output_dir, 'btc_holdings_vs_market_cap_scatter.png'))

    financial_leverage_ratio_plot = plot_financial_leverage_ratio(df)
    save_plot(financial_leverage_ratio_plot, os.path.join(output_dir, 'financial_leverage_ratio.png'))

    btc_to_net_assets_ratio_plot = plot_btc_to_net_assets_ratio(df)
    save_plot(btc_to_net_assets_ratio_plot, os.path.join(output_dir, 'btc_to_net_assets_ratio.png'))

    # Save the processed data
    output_data_path = os.path.join(output_dir, 'mstr_btc_metrics.csv')
    df.to_csv(output_data_path, index=False)
    print(f"Processed data saved to {output_data_path}")

    print(f"MSTR Shares Outstanding: {mstr_shares}")

if __name__ == "__main__":
    main()
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import yfinance as yf
import numpy as np

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def get_mstr_shares_outstanding():
    mstr = yf.Ticker("MSTR")
    return mstr.info['sharesOutstanding']

def calculate_values(df, mstr_shares):
    df['BTC_Total_Value'] = df['Total_BTC'] * df['BTC-USD_Close']
    df['MSTR_Total_Value'] = df['MSTR_Close'] * mstr_shares
    df['BTC_MSTR_Ratio'] = df['BTC_Total_Value'] / df['MSTR_Total_Value']
    df['Year'] = df['Date'].dt.year
    return df

def plot_total_values(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['BTC_Total_Value'], label='BTC Total Value')
    plt.plot(df['Date'], df['MSTR_Total_Value'], label='MSTR Total Value')
    plt.title('BTC Total Value vs MSTR Total Value')
    plt.xlabel('Date')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plot_BTC_MSTR_Ratio(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['BTC_MSTR_Ratio'])
    plt.title('BTC Total Value / MSTR Total Value Ratio')
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plot_scatter(df):
    plt.figure(figsize=(12, 8))
    years = df['Year'].unique()
    colors = plt.cm.rainbow(np.linspace(0, 1, len(years)))
    
    for year, color in zip(years, colors):
        year_data = df[df['Year'] == year]
        plt.scatter(year_data['BTC_Total_Value'], year_data['MSTR_Total_Value'], 
                    c=[color], label=str(year), alpha=0.6)
    
    # Add y=x dashed line
    max_value = max(df['BTC_Total_Value'].max(), df['MSTR_Total_Value'].max())
    plt.plot([0, max_value], [0, max_value], 'k--', alpha=0.5, label='y=x')
    
    plt.title('BTC Total Value vs MSTR Total Value (Scatter)')
    plt.xlabel('BTC Total Value (USD)')
    plt.ylabel('MSTR Total Value (USD)')
    plt.legend(title='Year')
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

    df = load_data(data_path)
    mstr_shares = get_mstr_shares_outstanding()
    df = calculate_values(df, mstr_shares)

    total_values_plot = plot_total_values(df)
    save_plot(total_values_plot, os.path.join(output_dir, 'total_values_comparison.png'))

    BTC_MSTR_Ratio_plot = plot_BTC_MSTR_Ratio(df)
    save_plot(BTC_MSTR_Ratio_plot, os.path.join(output_dir, 'BTC_MSTR_Ratio.png'))

    scatter_plot = plot_scatter(df)
    save_plot(scatter_plot, os.path.join(output_dir, 'BTC_MSTR_scatter.png'))

    # Save the processed data
    output_data_path = os.path.join(output_dir, 'mstr_btc_data.csv')
    df.to_csv(output_data_path, index=False)
    print(f"Processed data saved to {output_data_path}")

    print(f"MSTR Shares Outstanding: {mstr_shares}")

if __name__ == "__main__":
    main()
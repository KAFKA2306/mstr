import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import yfinance as yf

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
    df['Value_Ratio'] = df['MSTR_Total_Value'] / df['BTC_Total_Value']
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

def plot_value_ratio(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Value_Ratio'])
    plt.title('MSTR Total Value / BTC Total Value Ratio')
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

    df = load_data(data_path)
    mstr_shares = get_mstr_shares_outstanding()
    df = calculate_values(df, mstr_shares)

    total_values_plot = plot_total_values(df)
    save_plot(total_values_plot, os.path.join(output_dir, 'total_values_comparison.png'))

    value_ratio_plot = plot_value_ratio(df)
    save_plot(value_ratio_plot, os.path.join(output_dir, 'value_ratio.png'))

    # Save the processed data
    output_data_path = os.path.join(output_dir, 'processed_data.csv')
    df.to_csv(output_data_path, index=False)
    print(f"Processed data saved to {output_data_path}")

    print(f"MSTR Shares Outstanding: {mstr_shares}")

if __name__ == "__main__":
    main()
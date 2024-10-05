import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Remove timezone info
    df = df[['Date', 'Close']]
    df.columns = ['Date', f'{ticker}_Close']
    return df

def load_btc_holdings(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Remove timezone info
    return df

def fetch_financial_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    quarterly_data = stock.quarterly_financials
    balance_sheet = stock.quarterly_balance_sheet
    
    total_assets = balance_sheet.loc['Total Assets']
    total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest']
    
    financial_data = pd.DataFrame({
        'Date': total_assets.index,
        'Total_Assets': total_assets.values,
        'Total_Liabilities': total_liabilities.values
    })
    
    financial_data['Date'] = pd.to_datetime(financial_data['Date']).dt.tz_localize(None)
    financial_data = financial_data.sort_values('Date')
    
    return financial_data

def process_data(start_date, end_date, btc_holdings_path):
    # Fetch MSTR and BTC-USD data
    mstr_data = fetch_data("MSTR", start_date, end_date)
    btc_data = fetch_data("BTC-USD", start_date, end_date)
    
    # Fetch financial data
    financial_data = fetch_financial_data("MSTR", start_date, end_date)

    # Merge MSTR and BTC-USD data
    merged_data = pd.merge(mstr_data, btc_data, on='Date', how='outer')

    # Load BTC holdings data
    btc_holdings = load_btc_holdings(btc_holdings_path)

    # Merge with BTC holdings data
    final_data = pd.merge(merged_data, btc_holdings, on='Date', how='outer')
    
    # Merge with financial data
    final_data = pd.merge(final_data, financial_data, on='Date', how='outer')

    # Sort by date and forward fill missing values
    final_data = final_data.sort_values('Date').ffill()

    return final_data

def save_to_csv(df, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    # Set date range (e.g., last 5 years)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = '2020-03-01'
    # Set file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    btc_holdings_path = os.path.join(script_dir, '..', 'data', 'btcholdings.csv')
    output_path = os.path.join(script_dir, '..', 'data', 'mstr_btc_data.csv')

    try:
        # Process data
        combined_data = process_data(start_date, end_date, btc_holdings_path)

        # Save combined data
        save_to_csv(combined_data, output_path)
    except FileNotFoundError as e:
        print(f"Error: {e}. Please make sure the file exists and the path is correct.")
    except ValueError as e:
        print(f"Error processing data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
import yfinance as yf
import numpy as np

# ... (前の関数は変更なし)

def calculate_monthly_averages(df):
    # Convert Date to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Set Date as index
    df = df.set_index('Date')
    
    # Calculate monthly averages
    monthly_avg = df.resample('M').mean()
    
    # Reset index to make Date a column again
    monthly_avg = monthly_avg.reset_index()
    
    return monthly_avg

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'mstr_btc_data.csv')
    output_dir = os.path.join(script_dir, '..', 'output')
    
    os.makedirs(output_dir, exist_ok=True)

    df = load_mstr_btc_data(data_path)
    mstr_shares = get_mstr_shares_outstanding()
    df = calculate_mstr_btc_metrics(df, mstr_shares)

    # Calculate and save monthly averages
    monthly_avg_df = calculate_monthly_averages(df)
    monthly_avg_output_path = os.path.join(output_dir, 'mstr_btc_metrics_monthly_avg.csv')
    monthly_avg_df.to_csv(monthly_avg_output_path, index=False)
    print(f"Monthly average data saved to {monthly_avg_output_path}")

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

    # Save the processed daily data
    output_data_path = os.path.join(output_dir, 'mstr_btc_metrics_daily.csv')
    df.to_csv(output_data_path, index=False)
    print(f"Processed daily data saved to {output_data_path}")

    print(f"MSTR Shares Outstanding: {mstr_shares}")

if __name__ == "__main__":
    main()
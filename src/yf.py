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

def process_data(start_date, end_date, btc_holdings_path):
    # Fetch MSTR and BTC-USD data
    mstr_data = fetch_data("MSTR", start_date, end_date)
    btc_data = fetch_data("BTC-USD", start_date, end_date)

    # Merge MSTR and BTC-USD data
    merged_data = pd.merge(mstr_data, btc_data, on='Date', how='outer')

    # Load BTC holdings data
    btc_holdings = load_btc_holdings(btc_holdings_path)

    # Merge with BTC holdings data
    final_data = pd.merge(merged_data, btc_holdings, on='Date', how='outer')

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
    start_date = '2020-08-10'
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

if __name__ == "__main__":
    main()
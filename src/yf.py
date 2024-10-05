import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    df = df[['Date', 'Close']]
    df.columns = ['Date', f'{ticker}_Close']
    return df

def load_btc_holdings(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    return df

def fetch_financial_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
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

def get_mstr_shares_outstanding():
    mstr = yf.Ticker("MSTR")
    return mstr.info['sharesOutstanding']

def process_data(start_date, end_date, btc_holdings_path):
    mstr_data = fetch_stock_data("MSTR", start_date, end_date)
    btc_data = fetch_stock_data("BTC-USD", start_date, end_date)
    financial_data = fetch_financial_data("MSTR", start_date, end_date)
    btc_holdings = load_btc_holdings(btc_holdings_path)

    merged_data = pd.merge(mstr_data, btc_data, on='Date', how='outer')
    merged_data = pd.merge(merged_data, btc_holdings, on='Date', how='outer')
    final_data = pd.merge(merged_data, financial_data, on='Date', how='outer')

    final_data = final_data.sort_values('Date').ffill()
    return final_data

def calculate_metrics(df, mstr_shares):
    df['BTC_Holdings_Value_USD'] = df['Total_BTC'] * df['BTC-USD_Close']
    df['MSTR_Market_Cap_USD'] = df['MSTR_Close'] * mstr_shares
    df['BTC_to_Market_Cap_Ratio'] = df['BTC_Holdings_Value_USD'] / df['MSTR_Market_Cap_USD']
    df['Year'] = df['Date'].dt.year
    df['Financial_Leverage_Ratio'] = df['Total_Liabilities'] / df['Total_Assets']
    df['Net_Assets_USD'] = df['Total_Assets'] - df['Total_Liabilities']
    df['BTC_to_Net_Assets_Ratio'] = df['BTC_Holdings_Value_USD'] / df['Net_Assets_USD']
    return df

def calculate_monthly_averages(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    monthly_avg = df.resample('ME').mean()
    monthly_avg = monthly_avg.reset_index()
    return monthly_avg

def save_to_csv(df, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = '2020-03-01'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    btc_holdings_path = os.path.join(script_dir, '..', 'data', 'btcholdings.csv')
    output_dir = os.path.join(script_dir, '..', 'output')
    
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = process_data(start_date, end_date, btc_holdings_path)
        mstr_shares = get_mstr_shares_outstanding()
        df = calculate_metrics(df, mstr_shares)

        daily_output_path = os.path.join(output_dir, 'mstr_btc_metrics_daily.csv')
        save_to_csv(df, daily_output_path)

        monthly_avg_df = calculate_monthly_averages(df)
        monthly_avg_output_path = os.path.join(output_dir, 'mstr_btc_metrics_monthly_avg.csv')
        save_to_csv(monthly_avg_df, monthly_avg_output_path)

        print(f"MSTR Shares Outstanding: {mstr_shares}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
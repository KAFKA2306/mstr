import yfinance as yf
import pandas as pd
import numpy as np
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

def load_btc_holdings(file_path, start_date):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    return df[df['Date'] >= start_date]

def load_financial_data(file_path, start_date):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    return df[df['Date'] >= start_date]

def fetch_financial_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.quarterly_balance_sheet
    
    total_assets = balance_sheet.loc['Total Assets']
    
    financial_data = pd.DataFrame({
        'Date': total_assets.index,
        'Total_Assets': total_assets.values,
    })
    
    financial_data['Date'] = pd.to_datetime(financial_data['Date']).dt.tz_localize(None)
    financial_data = financial_data[financial_data['Date'] >= start_date]
    financial_data = financial_data.sort_values('Date')
    
    return financial_data

def get_mstr_shares_outstanding():
    mstr = yf.Ticker("MSTR")
    return mstr.info['sharesOutstanding']

def process_data(start_date, end_date, btc_holdings_path, financial_data_path):
    mstr_data = fetch_stock_data("MSTR", start_date, end_date)
    btc_data = fetch_stock_data("BTC-USD", start_date, end_date)
    assets_data = fetch_financial_data("MSTR", start_date, end_date)
    btc_holdings = load_btc_holdings(btc_holdings_path, start_date)
    financial_data = load_financial_data(financial_data_path, start_date)

    merged_data = pd.merge(mstr_data, btc_data, on='Date', how='outer')
    merged_data = pd.merge(merged_data, btc_holdings, on='Date', how='outer')
    merged_data = pd.merge(merged_data, assets_data, on='Date', how='outer')
    final_data = pd.merge(merged_data, financial_data, on='Date', how='outer')

    final_data = final_data.sort_values('Date')
    final_data = fill_data(final_data)
    return final_data[final_data['Date'] >= pd.to_datetime(start_date)]

def fill_data(df):
    for col in df.columns:
        if col != 'Date':
            df[col] = df[col].ffill()
    return df

def format_number(x, is_ratio=False):
    if pd.isnull(x):
        return np.nan
    if is_ratio:
        return float(f'{x:.4g}')
    else:
        return int(x)  # 小数点以下を切り捨てて整数に変換

def calculate_metrics(df, mstr_shares):
    # Calculate new columns
    df['MSTR_Market_Cap_USD'] = df['MSTR_Close'] * mstr_shares
    df['BTC_Holdings_Value_USD'] = df['Total_BTC'] * df['BTC-USD_Close']
    df['BTC_to_Market_Cap_Ratio'] = df['BTC_Holdings_Value_USD'] / df['MSTR_Market_Cap_USD']
    df['Financial_Leverage_Ratio'] = df['Total_Liabilities'] / df['Total_Assets']
    df['Net_Assets_USD'] = df['Total_Assets'] - df['Total_Liabilities']
    df['BTC_to_Net_Assets_Ratio'] = df['BTC_Holdings_Value_USD'] / df['Net_Assets_USD']
    df['Gross_Profit_Margin'] = df['Gross_Profit'] / df['MSTR_Market_Cap_USD']  # 新しい指標を追加

    # Identify ratio columns
    ratio_columns = ['BTC_to_Market_Cap_Ratio', 'Financial_Leverage_Ratio', 'BTC_to_Net_Assets_Ratio', 'Gross_Profit_Margin']

    # Apply formatting to all numeric columns
    for col in df.select_dtypes(include=[np.number]).columns:
        if col in ratio_columns:
            df[col] = df[col].apply(lambda x: format_number(x, is_ratio=True))
        else:
            df[col] = df[col].apply(lambda x: format_number(x, is_ratio=False))

    df['Year'] = df['Date'].dt.year
    
    return df

def calculate_monthly_averages(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    monthly_avg = df.resample('ME').mean()
    monthly_avg = monthly_avg.reset_index()
    
    # Re-apply formatting to monthly averages
    ratio_columns = ['BTC_to_Market_Cap_Ratio', 'Financial_Leverage_Ratio', 'BTC_to_Net_Assets_Ratio', 'Gross_Profit_Margin']
    for col in monthly_avg.select_dtypes(include=[np.number]).columns:
        if col in ratio_columns:
            monthly_avg[col] = monthly_avg[col].apply(lambda x: format_number(x, is_ratio=True))
        else:
            monthly_avg[col] = monthly_avg[col].apply(lambda x: format_number(x, is_ratio=False))
    
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
    financial_data_path = os.path.join(script_dir, '..', 'data', 'mstr_financial_data.csv')
    output_dir = os.path.join(script_dir, '..', 'output')
    
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = process_data(start_date, end_date, btc_holdings_path, financial_data_path)
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
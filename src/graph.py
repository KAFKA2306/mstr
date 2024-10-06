import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

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
    
    plt.title('MicroStrategy: Bitcoin Holdings Value vs Market Capitalization (Scatter)')
    plt.xlabel('Bitcoin Holdings Value (USD)')
    plt.ylabel('MicroStrategy Market Capitalization (USD)')
    plt.legend(title='Year')
    plt.tight_layout()
    return plt

def plot_market_cap_btc_value_total_liabilities(df):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(df['Date'], df['MSTR_Market_Cap_USD'], label='Market Capitalization')
    ax1.plot(df['Date'], df['BTC_Holdings_Value_USD'], label='Bitcoin Holdings Value')
    ax1.plot(df['Date'], df['Total_Liabilities'], label='Total Liabilities')
    ax1.plot(df['Date'], df['Gross_Profit'], label='Gross Profit', color='red')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Value (USD)')
    ax1.tick_params(axis='y')

    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1 , labels1, loc='upper left')

    plt.title('MicroStrategy: Market Cap, BTC Value, Total Liabilities, and Gross Profit')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def plot_market_cap_vs_total_liabilities_scatter(df):
    plt.figure(figsize=(12, 8))
    years = df['Year'].unique()
    colors = plt.cm.rainbow(np.linspace(0, 1, len(years)))
    
    for year, color in zip(years, colors):
        year_data = df[df['Year'] == year]
        plt.scatter(year_data['Total_Liabilities'], year_data['MSTR_Market_Cap_USD'], 
                    c=[color], label=str(year), alpha=0.6)
    
    max_value = max(df['Total_Liabilities'].max(), df['MSTR_Market_Cap_USD'].max())
    plt.plot([0, max_value], [0, max_value], 'k--', alpha=0.5, label='1:1 Line')
    
    plt.title('MicroStrategy: Market Capitalization vs Total Liabilities (Scatter)')
    plt.xlabel('Total Liabilities (USD)')
    plt.ylabel('MicroStrategy Market Capitalization (USD)')
    plt.legend(title='Year')
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
        (plot_btc_holdings_vs_market_cap_scatter, 'bitcoin_holdings_vs_market_cap_scatter.png'),
        (plot_market_cap_btc_value_total_liabilities, 'market_cap_bitcoin_value_total_liabilities_gross_profit.png'),
        (plot_market_cap_vs_total_liabilities_scatter, 'market_cap_vs_total_liabilities_scatter.png'),
    ]

    for plot_func, filename in plots:
        plt = plot_func(df)
        save_plot(plt, os.path.join(output_dir, filename))
        plt.close()

if __name__ == "__main__":
    main()
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_and_process_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])
    df['Year'] = df['Date'].dt.year
    df['net_value_btc_ratio'] = (df['MSTR_Market_Cap_USD'] - df['Total_Liabilities']) / df['BTC_Holdings_Value_USD']
    df['btc_holdings_yoy'] = df['Total_BTC'].pct_change(periods=365)
    return df

def plot_scatter(df, x, y, title, output):
    plt.figure(figsize=(12, 8))
    for year in df['Year'].unique():
        data = df[df['Year'] == year]
        plt.scatter(data[x], data[y], label=str(year), alpha=0.6)
    max_val = df[[x,y]].max().max()
    plt.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='1:1 Line')
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.legend(title='Year')
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

def plot_time_series(df, columns, title, output, y_range=None):
    plt.figure(figsize=(12, 6))
    for col in columns:
        plt.plot(df['Date'], df[col], label=col)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Value')
    if y_range:
        plt.ylim(y_range)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

def plot_dual_axis(df, title, output):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color1 = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Net Valueto BTC Ratio', color=color1)
    ax1.plot(df['Date'], df['net_value_btc_ratio'], color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 2)
    ax1.axhline(y=2, color=color1, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    color2 = 'tab:orange'
    ax2.set_ylabel('BTC Holdings YoY Change', color=color2)
    ax2.plot(df['Date'], df['btc_holdings_yoy'], color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 1)
    ax2.axhline(y=1, color=color2, linestyle='--', alpha=0.5)

    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

def main():
    input_file = 'output/mstr_btc_metrics_daily.csv'
    output_dir = 'output/plots'
    os.makedirs(output_dir, exist_ok=True)

    df = load_and_process_data(input_file)

    scatter_plots = [
        ('BTC_Holdings_Value_USD', 'MSTR_Market_Cap_USD', 'Bitcoin Holdings vs Market Cap', 'bitcoin_vs_market_cap.png'),
        ('Total_Liabilities', 'MSTR_Market_Cap_USD', 'Market Cap vs Total Liabilities', 'market_cap_vs_liabilities.png')
    ]

    time_series_plots = [
        (['MSTR_Market_Cap_USD', 'BTC_Holdings_Value_USD', 'Total_Liabilities', 'Gross_Profit'],
         'Key Financial Metrics Over Time', 'financial_metrics.png', None),
        (['Total_BTC'], 'Total Bitcoin Holdings Over Time', 'total_btc_holdings.png', None)
    ]

    for x, y, title, filename in scatter_plots:
        plot_scatter(df, x, y, title, f'{output_dir}/{filename}')

    for columns, title, filename, y_range in time_series_plots:
        plot_time_series(df, columns, title, f'{output_dir}/{filename}', y_range)

    plot_dual_axis(df, 'Net Value ( MSTR_Market_Cap_USD - Total_Liabilities )  to BTC Ratio & BTC Holdings YoY Change', f'{output_dir}/mstr_btc_metrics_dual_axis.png')

    print("All plots generated and saved.")

if __name__ == "__main__":
    main()
import ccxt
import time
import pandas as pd
from datetime import datetime, timedelta

LARGE_GRAPHS = True

# Function to calculate APY from the 8-hour funding rate
def calculate_apy_from_8hr_funding_rate(funding_rate_8hr):
    funding_frequency_per_day = 3  # 3 funding periods per day (every 8 hours)
    daily_rate = (1 + funding_rate_8hr) ** funding_frequency_per_day - 1
    yearly_rate = (1 + daily_rate) ** 365 - 1  # Compounded daily for a year
    return yearly_rate * 100  # Return as percentage


# Function to fetch historical funding rate from a given exchange for the last 7 days
def get_funding_rate_history(exchange, symbol):
    exchange_class = getattr(ccxt, exchange)()
    markets = exchange_class.load_markets()
    if symbol in markets:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        seven_days_ago_ms = int(seven_days_ago.timestamp() * 1000)  # Convert to milliseconds
        funding_rate_history = exchange_class.fetch_funding_rate_history(symbol, since=seven_days_ago_ms)
        return funding_rate_history
    else:
        raise ValueError(f"Market {symbol} not found on {exchange}.")


# Function to calculate the 7-day average funding rate
def calculate_7day_average_funding_rate(funding_rate_history):
    last_7_days_rates = [entry['fundingRate'] for entry in funding_rate_history]
    if last_7_days_rates:
        return sum(last_7_days_rates) / len(last_7_days_rates)
    else:
        return None


# Function to get the most recent funding rate
def get_most_recent_funding_rate(funding_rate_history):
    return funding_rate_history[-1]['fundingRate'] if funding_rate_history else None

def calculate_apy_history(funding_rate_history):
    return [calculate_apy_from_8hr_funding_rate(rate['fundingRate']) for rate in funding_rate_history]


# Function to calculate and display results for a list of exchanges and markets
def display_results(exchanges_symbols):
    data = []

    for exchange, symbol in exchanges_symbols:
        try:
            funding_rate_history = get_funding_rate_history(exchange, symbol)
            avg_funding_rate_7d = calculate_7day_average_funding_rate(funding_rate_history)
            most_recent_rate = get_most_recent_funding_rate(funding_rate_history)
            historical_rates = [entry['fundingRate'] for entry in funding_rate_history]
            historical_dates = [entry['datetime'] for entry in funding_rate_history]  # Grab the datetime for the x-axis

            historical_apy = [calculate_apy_from_8hr_funding_rate(rate) for rate in historical_rates]

            if avg_funding_rate_7d is not None:
                apy = calculate_apy_from_8hr_funding_rate(most_recent_rate)
                data.append({
                    'Exchange': exchange.capitalize(),
                    'Market': symbol,
                    'Most Recent Funding Rate (8hr)': f"{100*most_recent_rate:.4f}%",
                    '7-Day Avg Funding Rate (8hr)': f"{100*avg_funding_rate_7d:.4f}%",
                    'APY': f"{apy:.2f}%",
                    'Historical APY': historical_apy
                })

                # # Visualize the funding rate history as a line chart
                # st.line_chart(pd.DataFrame({
                #     'Funding Rate': historical_rates
                # }, index=pd.to_datetime(historical_dates)))

            else:
                data.append({
                    'Exchange': exchange.capitalize(),
                    'Market': symbol,
                    'Most Recent Funding Rate (8hr)': 'N/A',
                    '7-Day Avg Funding Rate (8hr)': 'N/A',
                    'APY': 'N/A',
                    'Historical APY': [None]
                })
        except Exception as e:
            data.append({
                'Exchange': exchange.capitalize(),
                'Market': symbol,
                'Most Recent Funding Rate (8hr)': 'N/A',
                '7-Day Avg Funding Rate (8hr)': 'N/A',
                'APY': 'N/A',
                'Historical APY': [None]
            })
        # time.sleep(3)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    return df

# Function to display charts for each exchange/market
def display_charts(exchanges_symbols):
    for exchange, symbol in exchanges_symbols:
        try:
            # Fetch the historical funding rates
            funding_rate_history = get_funding_rate_history(exchange, symbol)

            # Get the most recent funding rate and APY
            most_recent_rate = get_most_recent_funding_rate(funding_rate_history)
            most_recent_apy = calculate_apy_from_8hr_funding_rate(most_recent_rate)

            # Calculate the APY history based on the funding rates
            apy_history = calculate_apy_history(funding_rate_history)
            historical_dates = [entry['datetime'] for entry in funding_rate_history]

            # Add title with exchange name, most recent funding rate, and APY
            st.subheader(f"{exchange.capitalize()} - Funding Rate: {100*most_recent_rate:.4f}% APY: {most_recent_apy:.2f}%")

            # Create a line chart for the APY history
            st.line_chart(pd.DataFrame({
                'APY (%)': apy_history
            }, index=pd.to_datetime(historical_dates)))

        except Exception as e:
            st.error(f"Error fetching data for {exchange.capitalize()} - {symbol}: {e}")



# Main function for standalone script mode
def main():
    # Define the exchanges and symbols you want to check
    exchanges_symbols = [
        # ('krakenfutures', 'TAO/USD:USD'),
        ('binance', 'TAO/USDT:USDT'),
        # ('deribit', 'ETH/USDC:USDC'),
        ('bybit', 'TAO/USDT:USDT'),
        # ('okx', 'TAO/USDT:USDT')
    ]

    # Iterate over each exchange and symbol and display the results
    df = display_results(exchanges_symbols)
    print(df.to_string(index=False))
    # render_table_with_sparklines(df)



# Streamlit UI
if __name__ == '__main__':
    import sys

    if "streamlit" in sys.modules:
        print('running streamlit')
        import streamlit as st

        # st.set_page_config(layout="wide")
        st.title("Perpetual Futures APY Calculator")
        st.text("Positive funding rate / apy; Longs pay shorts")

        # Define available exchanges and markets
        exchanges_symbols = [
            # ('krakenfutures', 'TAO/USD:USD'),
            ('binance', 'TAO/USDT:USDT'),
            # ('deribit', 'ETH/USDC:USDC'),
            ('bybit', 'TAO/USDT:USDT'),
            # ('okx', 'TAO/USDT:USDT')
        ]

        # Display charts for each exchange

        if LARGE_GRAPHS:
            display_charts(exchanges_symbols)
        else:
            # Automatically fetch and display results for all exchanges
            df = display_results(exchanges_symbols)
            st.dataframe(df, column_config={
                "Historical APY": st.column_config.LineChartColumn("Historical APY", width="medium")
            })

    else:
        print("not running in streamlit")
        main()  # Runs in PyCharm or any other standard Python environment


# TODO: There's some issue when running on production that data for some exchanges isn't fetched fast enough
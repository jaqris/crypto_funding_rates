import ccxt
import streamlit as st


def calculate_apy_from_funding_rate(funding_rate, funding_frequency):
    """
    Calculate the APY (Annual Percentage Yield) from the funding rate and funding frequency.
    """
    daily_rate = (1 + funding_rate) ** funding_frequency - 1
    yearly_rate = (1 + daily_rate) ** 365 - 1  # 365 days in a year
    return yearly_rate * 100  # Convert to percentage


def get_kraken_funding_rate():
    """
    Fetch the funding rate for Kraken ETH/USD perpetual futures market.
    """
    kraken_futures = ccxt.krakenfutures()

    # Load markets and select the perpetual ETH/USD market
    markets = kraken_futures.load_markets()
    symbol = 'ETH/USD:USD'

    if symbol in markets:
        funding_rate_info = kraken_futures.fetch_funding_rate(symbol)
        funding_rate = funding_rate_info['fundingRate']
        return funding_rate
    else:
        raise ValueError(f"Market {symbol} not found on Kraken Futures.")


# Streamlit UI
st.title("Kraken ETH/USD Perpetual Futures APY Calculator")

funding_frequency = 3  # Kraken charges funding every 8 hours

if st.button('Calculate APY'):
    try:
        funding_rate = get_kraken_funding_rate()
        apy = calculate_apy_from_funding_rate(funding_rate, funding_frequency)

        st.write(f"Funding Rate: {funding_rate:.6f}")
        st.write(f"Annual Percentage Yield (APY): {apy:.2f}%")
    except Exception as e:
        st.error(f"Error: {e}")

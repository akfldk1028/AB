from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="MinimalServer", host="0.0.0.0", port=3000)


@mcp.tool()
def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
):
    """Exchange rate tool with realistic demo data for various currency pairs.

    Args:
        currency_from: Source currency (e.g. "USD", "EUR", "GBP", "JPY", "KRW").
        currency_to: Target currency (e.g. "USD", "EUR", "GBP", "JPY", "KRW").
        currency_date: Date for exchange rate or "latest". Default "latest".

    Returns:
        Dictionary with exchange rate data.
    """
    print(f"🎉 MCP TOOL CALLED! Converting {currency_from} to {currency_to}")
    # Realistic demo exchange rates (as of 2024)
    exchange_rates = {
        "USD": {
            "EUR": 0.92,
            "GBP": 0.79, 
            "JPY": 149.50,
            "KRW": 1320.00,
            "CAD": 1.35,
            "AUD": 1.52,
            "CHF": 0.88,
            "CNY": 7.23
        },
        "EUR": {
            "USD": 1.09,
            "GBP": 0.86,
            "JPY": 162.80,
            "KRW": 1435.00,
            "CAD": 1.47,
            "AUD": 1.66,
            "CHF": 0.96,
            "CNY": 7.87
        },
        "GBP": {
            "USD": 1.27,
            "EUR": 1.16,
            "JPY": 189.00,
            "KRW": 1670.00,
            "CAD": 1.71,
            "AUD": 1.93,
            "CHF": 1.11,
            "CNY": 9.16
        },
        "JPY": {
            "USD": 0.0067,
            "EUR": 0.0061,
            "GBP": 0.0053,
            "KRW": 8.83,
            "CAD": 0.0090,
            "AUD": 0.0102,
            "CHF": 0.0059,
            "CNY": 0.0485
        },
        "KRW": {
            "USD": 0.00076,
            "EUR": 0.00070,
            "GBP": 0.00060,
            "JPY": 0.113,
            "CAD": 0.00102,
            "AUD": 0.00115,
            "CHF": 0.00067,
            "CNY": 0.00548
        }
    }
    
    # Normalize currency codes to uppercase
    currency_from = currency_from.upper()
    currency_to = currency_to.upper()
    
    # Handle same currency conversion
    if currency_from == currency_to:
        rate = 1.0
    else:
        # Get the rate from our demo data
        rate = exchange_rates.get(currency_from, {}).get(currency_to)
        
        # If direct rate not found, try inverse
        if rate is None:
            inverse_rate = exchange_rates.get(currency_to, {}).get(currency_from)
            if inverse_rate:
                rate = 1.0 / inverse_rate
            else:
                # Default fallback rate
                rate = 1.0
    
    return {
        "success": True,
        "amount": 1,
        "base": currency_from,
        "target": currency_to,
        "date": "2024-08-16" if currency_date == "latest" else currency_date,
        "rate": rate,
        "result": f"1 {currency_from} = {rate:.4f} {currency_to}",
        "provider": "Demo Exchange Rate Service"
    }


if __name__ == "__main__":
    mcp.run(transport="sse")
PRICES = {
    "gpt-4o": {
        "input": 0.00125,
        "output": 0.00500
    },
    "gpt-4o-mini": {
        "input": 0.000075,
        "output": 0.000300
    }
}

def get_prices(model: str, usage: dict) -> dict:

    if model not in PRICES:
        raise ValueError(f"Model {model} is not supported")

    prices = PRICES[model]

    input_price = prices["input"] * usage["prompt_tokens"] / 1000
    output_price = prices["output"] * usage["completion_tokens"] / 1000

    return {
        "input": input_price,
        "output": output_price,
    }
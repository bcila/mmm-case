from decimal import Decimal, ROUND_HALF_UP

def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    quantize_exp = Decimal('1.' + ('0' * places))
    return value.quantize(quantize_exp, rounding=ROUND_HALF_UP)

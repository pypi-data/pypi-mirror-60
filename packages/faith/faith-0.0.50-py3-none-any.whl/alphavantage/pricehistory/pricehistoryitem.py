from typing import Any
from typing import Dict


class PriceHistoryItem(object):

    def __init__(
        self,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
        adjusted_close_price: float,
        volume: float,
        dividend_amount: float,
        split_coefficient: float,
    ) -> None:
        self._open_price = open_price
        self._high_price = high_price
        self._low_price = low_price
        self._close_price = close_price
        self._adjusted_close_price = adjusted_close_price
        self._volume = volume
        self._dividend_amount = dividend_amount
        self._split_coefficient = split_coefficient

    @property
    def open_price(self) -> float:
        return self._open_price

    @property
    def close_price(self) -> float:
        return self._close_price

    @property
    def high_price(self) -> float:
        return self._high_price

    @property
    def low_price(self) -> float:
        return self._low_price

    @property
    def adjusted_open_price(self) -> float:
        return self.open_price / (self.close_price / self.adjusted_close_price)

    @property
    def adjusted_close_price(self) -> float:
        return self._adjusted_close_price

    @property
    def adjusted_high_price(self) -> float:
        return self._high_price / (self.close_price / self.adjusted_close_price)

    @property
    def adjusted_low_price(self) -> float:
        return self._low_price / (self.close_price / self.adjusted_close_price)

    @property
    def volume(self) -> float:
        return self._volume


def price_history_item_from_data(data: Dict[str, Any]) -> PriceHistoryItem:
    return PriceHistoryItem(
        open_price=float(data['1. open']),
        high_price=float(data['2. high']),
        low_price=float(data['3. low']),
        close_price=float(data['4. close']),
        adjusted_close_price=float(data['5. adjusted close']),
        volume=float(data['6. volume']),
        dividend_amount=float(data['7. dividend amount']),
        split_coefficient=float(data['8. split coefficient']),
    )

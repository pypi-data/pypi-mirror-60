from copy import copy
from typing import Dict
from typing import List
from typing import Optional

from report.symbolhistory.symbolhistorycontextholding import SymbolHistoryContextHolding
from report.symbolhistory.symbolhistorycontextsnapshot import SymbolHistoryContextSnapshot
from report.symbolhistory.symbolhistoryevent import SymbolHistoryEvent
from robinhood.lib.marketplace.optioninstrument import OptionInstrument


class SymbolHistoryContext(object):

    def __init__(self, symbol: str) -> None:
        self._profit = 0.0
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=symbol,
            quantity=0,
            avg_unit_price=0.0,
            option_instrument=None,
        )
        self._option_sell_holding: Dict[str, SymbolHistoryContextHolding] = {}
        self._option_buy_holding: Dict[str, SymbolHistoryContextHolding] = {}
        self._tmp_call_assignment: List[SymbolHistoryContextHolding] = []
        self._tmp_stock_sold: Optional[SymbolHistoryContextHolding] = None

    @property
    def stock_cost_basis(self) -> float:
        return self._stock_holding.quantity * self._stock_holding.avg_unit_price

    @property
    def option_sell_holding(self) -> Dict[str, SymbolHistoryContextHolding]:
        return self._option_sell_holding

    @property
    def option_buy_holding(self) -> Dict[str, SymbolHistoryContextHolding]:
        return self._option_buy_holding

    def take_snapshot(self) -> SymbolHistoryContextSnapshot:
        return SymbolHistoryContextSnapshot(
            profit=self._profit,
            stock_holding=self._stock_holding,
            option_sell_holding=copy(self._option_sell_holding),
            option_buy_holding=copy(self._option_buy_holding),
        )

    def limit_or_market_buy_stock(self, quantity: int, price: float) -> None:
        total_cost = self.stock_cost_basis + quantity * price
        total_quantity = self._stock_holding.quantity + quantity
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity + quantity,
            avg_unit_price=total_cost / total_quantity,
            option_instrument=None,
        )

    def limit_or_market_sell_stock(self, quantity: int, price: float) -> None:
        self._profit += (price - self._stock_holding.avg_unit_price) * quantity
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity - quantity,
            avg_unit_price=self._stock_holding.avg_unit_price,
            option_instrument=None,
        )

    def sell_to_open(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
        option_instrument: OptionInstrument,
    ) -> None:
        self._buy_or_sell_to_open(
            buy_or_sell='sell',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
            option_instrument=option_instrument,
        )

    def buy_to_close(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
    ) -> None:
        self._buy_or_sell_to_close(
            buy_or_sell='buy',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
        )

    def buy_to_open(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
        option_instrument: OptionInstrument,
    ) -> None:
        self._buy_or_sell_to_open(
            buy_or_sell='buy',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
            option_instrument=option_instrument,
        )

    def sell_to_close(
        self,
        symbol: str,
        quantity: int,
        unit_price: float,
    ) -> None:
        self._buy_or_sell_to_close(
            buy_or_sell='sell',
            symbol=symbol,
            quantity=quantity,
            unit_price=unit_price,
        )

    def call_assignment(self, symbol: str, quantity: int, price: float, event: SymbolHistoryEvent) -> None:
        holding = self._option_sell_holding[symbol]
        current_avg_unit_price = holding.avg_unit_price
        new_quantity = holding.quantity - quantity
        if new_quantity == 0:
            del self._option_sell_holding[symbol]
        else:
            self._option_sell_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

        shares_sold = quantity * 100
        if self._stock_holding.quantity - shares_sold < 0:
            new_unit_price = price + current_avg_unit_price
            self._tmp_call_assignment.append(
                SymbolHistoryContextHolding(
                    symbol=symbol,
                    quantity=quantity,
                    avg_unit_price=new_unit_price,
                    option_instrument=None,
                ),
            )
            event.unit_price = new_unit_price
            return

        profit_per_share = price - self._stock_holding.avg_unit_price + current_avg_unit_price
        self._profit += profit_per_share * shares_sold
        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=self._stock_holding.quantity - shares_sold,
            avg_unit_price=self._stock_holding.avg_unit_price,
            option_instrument=None,
        )

    def put_assignment(
        self,
        symbol: str,
        num_of_contracts: int,
        strike_price: float,
    ) -> None:
        """
        This function makes changes to the portfolio when a put assignment event
        happens.

        Arguments:
            symbol: the symbol of the option instrument being assigned.
            num_of_contracts: the number of contracts being assigned.
            strike_price: the strike price of the contracts being assigned.
        """
        holding = self._option_sell_holding[symbol]
        new_quantity = holding.quantity - num_of_contracts
        if new_quantity == 0:
            del self._option_sell_holding[symbol]
        else:
            self._option_sell_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

        shares_bought = num_of_contracts * 100
        shares_avg_unit_cost = strike_price - holding.avg_unit_price
        shares_cost_basis = shares_avg_unit_cost * shares_bought
        if self._tmp_stock_sold is None:
            new_shares_holding = self._stock_holding.quantity + shares_bought
            avg_unit_price = (
                (self.stock_cost_basis + shares_cost_basis)
                / (self._stock_holding.quantity + shares_bought)
            )
        elif self._tmp_stock_sold.quantity >= shares_bought:
            new_shares_holding = self._stock_holding.quantity
            avg_unit_price = self._stock_holding.avg_unit_price
            profit = (self._tmp_stock_sold.avg_unit_price - shares_avg_unit_cost) * shares_bought
            self._profit += profit
            self._tmp_stock_sold = SymbolHistoryContextHolding(
                symbol=self._stock_holding.symbol,
                quantity=self._tmp_stock_sold.quantity - shares_bought,
                avg_unit_price=self._tmp_stock_sold.avg_unit_price,
                option_instrument=None,
            )
            if self._tmp_stock_sold.quantity == 0:
                self._tmp_stock_sold = None
        else:
            assert self._tmp_stock_sold.quantity < shares_bought
            new_shares_holding = shares_bought - self._tmp_stock_sold.quantity
            avg_unit_price = shares_avg_unit_cost
            profit = (self._tmp_stock_sold.avg_unit_price - shares_avg_unit_cost) * self._tmp_stock_sold.quantity
            self._profit += profit
            self._tmp_stock_sold = None

        self._stock_holding = SymbolHistoryContextHolding(
            symbol=self._stock_holding.symbol,
            quantity=new_shares_holding,
            avg_unit_price=avg_unit_price,
            option_instrument=None,
        )

    def put_exercise(
        self,
        symbol: str,
        num_of_contracts: int,
        avg_unit_price: float,
        strike_price: float,
    ) -> None:
        """
        This function makes changes to the portfolio when a put exercise event
        happens.

        Arguments:
            symbol: the symbol of the option instrument being exercised.
            num_of_contracts: the number of contracts being exercised.
            avg_unit_price: the average unit price of the contracts being exercised.
            strike_price: the strike price of the contracts being exercised.
        """
        shares_sold = num_of_contracts * 100
        share_sold_price = strike_price - avg_unit_price
        if self._stock_holding.quantity >= shares_sold:
            profit = (self._stock_holding.avg_unit_price - share_sold_price) * shares_sold
            self._profit += profit
            self._stock_holding = SymbolHistoryContextHolding(
                symbol=self._stock_holding.symbol,
                quantity=self._stock_holding.quantity - shares_sold,
                avg_unit_price=self._stock_holding.avg_unit_price,
                option_instrument=None,
            )
        else:
            cost_basis = shares_sold * share_sold_price

            if self._tmp_stock_sold is None:
                existing_quantity = 0
            else:
                existing_quantity = self._tmp_stock_sold.quantity
                cost_basis += self._tmp_stock_sold.avg_unit_price * existing_quantity

            self._tmp_stock_sold = SymbolHistoryContextHolding(
                symbol=self._stock_holding.symbol,
                quantity=existing_quantity + shares_sold,
                avg_unit_price=cost_basis / shares_sold,
                option_instrument=None,
            )

        holding = self._option_buy_holding[symbol]
        new_quantity = holding.quantity - num_of_contracts
        if new_quantity == 0:
            del self._option_buy_holding[symbol]
        else:
            self._option_buy_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

    def _call_exercise_for_assignment(
        self,
        symbol: str,
        quantity: int,
        price: float,
        strike_price: float,
    ) -> bool:
        for holding in self._tmp_call_assignment:
            if holding.quantity == quantity:
                profit = (holding.avg_unit_price - strike_price - price) * quantity * 100
                self._profit += profit
                del holding
                return True

        return False

    def call_exercise(
        self,
        symbol: str,
        quantity: int,
        price: float,
        strike_price: float,
    ) -> None:
        if not self._call_exercise_for_assignment(
            symbol=symbol,
            quantity=quantity,
            price=price,
            strike_price=strike_price,
        ):
            shares_bought = quantity * 100
            effective_cost_per_share = strike_price + price
            new_cost = effective_cost_per_share * shares_bought
            total_cost = self.stock_cost_basis + new_cost
            new_quantity = self._stock_holding.quantity + shares_bought
            avg_unit_price = 0.0 if new_quantity == 0.0 else total_cost / new_quantity

            self._stock_holding = SymbolHistoryContextHolding(
                symbol=self._stock_holding.symbol,
                quantity=new_quantity,
                avg_unit_price=avg_unit_price,
                option_instrument=None,
            )

        holding = self._option_buy_holding[symbol]
        new_quantity = holding.quantity - quantity
        if new_quantity == 0:
            del self._option_buy_holding[symbol]
        else:
            self._option_buy_holding[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=holding.avg_unit_price,
                option_instrument=holding.option_instrument,
            )

    def option_expire(self, symbol: str, quantity: int) -> None:
        if symbol in self._option_buy_holding:
            holding_dict = self._option_buy_holding
            holding = self._option_buy_holding[symbol]
            profit = -holding.quantity * holding.avg_unit_price * 100
        elif symbol in self._option_sell_holding:
            holding_dict = self._option_sell_holding
            holding = self._option_sell_holding[symbol]
            profit = holding.quantity * holding.avg_unit_price * 100
        else:
            return

        assert holding.quantity - quantity == 0
        del holding_dict[symbol]
        self._profit += profit

    def _buy_or_sell_to_open(
        self,
        buy_or_sell: str,
        symbol: str,
        quantity: int,
        unit_price: float,
        option_instrument: OptionInstrument,
    ) -> None:
        if buy_or_sell == 'buy':
            option_holding_dict = self._option_buy_holding
        else:
            option_holding_dict = self._option_sell_holding

        if symbol in option_holding_dict:
            holding = option_holding_dict[symbol]
            new_quantity = holding.quantity + quantity
            new_price = (holding.quantity * holding.avg_unit_price + quantity * unit_price) / new_quantity
        else:
            new_quantity = quantity
            new_price = unit_price

        option_holding_dict[symbol] = SymbolHistoryContextHolding(
            symbol=symbol,
            quantity=new_quantity,
            avg_unit_price=new_price,
            option_instrument=option_instrument,
        )

    def _buy_or_sell_to_close(
        self,
        buy_or_sell: str,
        symbol: str,
        quantity: int,
        unit_price: float,
    ) -> None:
        if buy_or_sell == 'buy':
            option_holding_dict = self._option_sell_holding
            unit_profit = option_holding_dict[symbol].avg_unit_price - unit_price
        else:
            option_holding_dict = self._option_buy_holding
            unit_profit = unit_price - option_holding_dict[symbol].avg_unit_price

        new_quantity = option_holding_dict[symbol].quantity - quantity
        self._profit += quantity * unit_profit * 100
        if new_quantity == 0:
            del option_holding_dict[symbol]
        else:
            option_holding_dict[symbol] = SymbolHistoryContextHolding(
                symbol=symbol,
                quantity=new_quantity,
                avg_unit_price=option_holding_dict[symbol].avg_unit_price,
                option_instrument=option_holding_dict[symbol].option_instrument,
            )

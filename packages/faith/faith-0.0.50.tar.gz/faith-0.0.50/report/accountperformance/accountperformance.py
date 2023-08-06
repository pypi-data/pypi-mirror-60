from collections import defaultdict
from typing import DefaultDict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import TYPE_CHECKING

from pandas import DataFrame
from terminaltables import AsciiTable

from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import get_event_date_format_func

if TYPE_CHECKING:
    from report.symbolhistory.symbolhistory import SymbolHistory


class AccountPerformance(object):

    def __init__(self, symbol_history: 'SymbolHistory') -> None:
        self._symbol_history = symbol_history

    def show(self, interval: str, symbol: Optional[str] = None) -> None:
        assert interval in {'Week', 'Month', 'All Time'}
        print(self._gen_reports(interval=interval, symbol=symbol))

    def _gen_reports(self, interval: str, symbol: Optional[str] = None) -> str:
        data = self._gen_data(interval=interval, symbol=symbol)
        t = AsciiTable(data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'center',
            1: 'right',
            2: 'right',
            3: 'right',
        }

        return str(t.table)

    def gen_df(self, interval: str) -> DataFrame:
        event_date_func = get_event_date_format_func(interval=interval)

        stock_profit: DefaultDict[str, DefaultDict[str, float]] = defaultdict(lambda: defaultdict(float))
        option_profit: DefaultDict[str, DefaultDict[str, float]] = defaultdict(lambda: defaultdict(float))

        for symbol, events in self._symbol_history.events_by_symbol.items():
            for i in range(1, len(events)):
                previous_event = events[i - 1]
                current_event = events[i]
                diff = current_event.context.profit - previous_event.context.profit
                if diff != 0:
                    event_date = event_date_func(current_event.event_ts)

                    if current_event.event_name in {
                        'BUY TO CLOSE',
                        'CUSTOM',
                        'CUSTOM CLOSE',
                        'FIG LEAF CLOSE',
                        'IRON CONDOR CLOSE',
                        'LONG CALL CLOSE',
                        'LONG CALL SPREAD CLOSE',
                        'LONG PUT CLOSE',
                        'LONG PUT SPREAD CLOSE',
                        'OPTION EXPIRATION',
                        'ROLLING SHORT CALL SPREAD',
                        'SHORT CALL SPREAD CLOSE',
                        'SHORT PUT SPREAD CLOSE',
                        'CALL CALENDAR SPREAD CLOSE',
                    }:
                        option_profit[symbol][event_date] += diff
                    elif current_event.event_name in {
                        'CALL ASSIGNMENT',
                        'LIMIT SELL',
                        'MARKET SELL',
                    }:
                        stock_profit[symbol][event_date] += diff
                    else:
                        raise Exception(f'Unrecognized event name: {current_event.event_name}')

        combined_data: DefaultDict[Tuple[str, str], Tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))
        for symbol, stock_profit_by_symbol in stock_profit.items():
            for interval, profit in stock_profit_by_symbol.items():
                combined_data[(interval, symbol)] = (
                    combined_data[(interval, symbol)][0] + profit,
                    combined_data[(interval, symbol)][1],
                )

        for symbol, option_profit_by_symbol in option_profit.items():
            for interval, profit in option_profit_by_symbol.items():
                combined_data[(interval, symbol)] = (
                    combined_data[(interval, symbol)][0],
                    combined_data[(interval, symbol)][1] + profit,
                )

        data = []
        for (interval, symbol), (_stock_profit, _option_profit) in combined_data.items():
            data.append([
                interval,
                symbol,
                _stock_profit,
                _option_profit,
                _stock_profit + _option_profit,
            ])

        return DataFrame(
            data=data,
            columns=[
                'interval',
                'symbol',
                'stock_profit',
                'option_profit',
                'total_profit',
            ],
        )

    def _gen_data(self, interval: str, symbol: Optional[str] = None) -> List[List[str]]:
        event_date_func = get_event_date_format_func(interval=interval)

        data = [[
            interval,
            'Settled Profit from Stock',
            'Settled Profit from Option',
            'Total Settled Profit',
        ]]

        stock_profit: DefaultDict[str, float] = defaultdict(float)
        option_profit: DefaultDict[str, float] = defaultdict(float)

        for _symbol, events in self._symbol_history.events_by_symbol.items():
            if symbol is not None and symbol != _symbol:
                continue

            for i in range(1, len(events)):
                previous_event = events[i - 1]
                current_event = events[i]
                diff = current_event.context.profit - previous_event.context.profit
                if diff != 0:
                    event_date = event_date_func(current_event.event_ts)

                    if current_event.event_name in {
                        'BUY TO CLOSE',
                        'CUSTOM',
                        'CUSTOM CLOSE',
                        'FIG LEAF CLOSE',
                        'IRON CONDOR CLOSE',
                        'LONG CALL CLOSE',
                        'LONG CALL SPREAD CLOSE',
                        'LONG PUT CLOSE',
                        'LONG PUT SPREAD CLOSE',
                        'OPTION EXERCISE',
                        'OPTION EXPIRATION',
                        'ROLLING SHORT CALL SPREAD',
                        'SHORT CALL SPREAD CLOSE',
                        'SHORT PUT SPREAD CLOSE',
                        'CALL CALENDAR SPREAD CLOSE',
                        'PUT ASSIGNMENT',
                    }:
                        option_profit[event_date] += diff
                    elif current_event.event_name in {
                        'CALL ASSIGNMENT',
                        'LIMIT SELL',
                        'MARKET SELL',
                    }:
                        stock_profit[event_date] += diff
                    else:
                        raise Exception(
                            f'{_symbol} {event_date} '
                            f'Unrecognized event name: {current_event.event_name}',
                        )

        all_dates: Set[str] = set()
        for event_date in stock_profit.keys():
            all_dates.add(event_date)
        for event_date in option_profit.keys():
            all_dates.add(event_date)

        for event_date in sorted(list(all_dates)):
            total_profit = stock_profit[event_date] + option_profit[event_date]
            data.append([
                event_date,
                format_price(stock_profit[event_date]),
                format_price(option_profit[event_date]),
                format_price(total_profit),
            ])

        return data

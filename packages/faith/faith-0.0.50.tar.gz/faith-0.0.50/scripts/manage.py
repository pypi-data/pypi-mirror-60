import click


@click.command()
def calc_stock_weekly_pct_chg_sd() -> None:
    from scripts.calcstockweeklypctchgsd import CalcStockWeeklyPctChgSd
    CalcStockWeeklyPctChgSd().run()


@click.command()
def run_option_sell_screener() -> None:
    from scripts.optionsellscreener import OptionSellScreener
    OptionSellScreener().run()


@click.command()
def slack_earning_report() -> None:
    from scripts.earningreport import EarningReport
    EarningReport().run()


@click.group()
def manage() -> None:
    pass


manage.add_command(calc_stock_weekly_pct_chg_sd)
manage.add_command(run_option_sell_screener)
manage.add_command(slack_earning_report)

if __name__ == '__main__':
    manage()

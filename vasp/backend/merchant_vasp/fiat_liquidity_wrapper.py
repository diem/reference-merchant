from diem_utils.sdks import liquidity
from diem_utils.types.liquidity.currency import CurrencyPair, CurrencyPairs, Currency
from diem_utils.types.liquidity.trade import Direction

from diem_utils.types.liquidity.currency import CurrencyPair, Currency
from diem_utils.precise_amount import Amount

import logging


class FiatLiquidityWrapper:
    def __init__(self, base_currency):
        self.liquidity_provider = liquidity.LpClient()
        self.base_currency = base_currency

    def quote(self, quote_currency, amount):
        if quote_currency == self.base_currency:
            raise ValueError(
                f"Unsupported quote: {self.base_currency} to {quote_currency}"
            )

        try:
            # fiat currencies are always the second in pairs
            currency_pair = CurrencyPair(
                Currency(quote_currency), Currency(self.base_currency)
            )
            _ = CurrencyPairs.from_pair(currency_pair)
        except KeyError:
            logging.warning(
                f"Could not get quote from {self.base_currency} to {quote_currency}"
            )
            return None
        return self.liquidity_provider.get_quote(
            currency_pair,
            amount,
        )

    def quote_price(self, quote_currency, amount):
        quote = self.quote(quote_currency, amount)

        unit = Amount().deserialize(Amount.unit)
        rate = unit / Amount().deserialize(quote.rate.rate)
        return (rate * Amount().deserialize(amount)).serialize()

    def pay_out(self, target_currency, amount, diem_deposit_address):
        quote = self.liquidity_provider.get_quote(
            CurrencyPair(Currency(self.base_currency), Currency(target_currency)),
            amount,
        )
        trade_id = self.liquidity_provider.trade_and_execute(
            quote.quote_id, Direction.Sell, diem_deposit_address
        )
        logging.debug(
            f"Sending payout: {quote.quote_id}, {Direction.Sell}, {diem_deposit_address} -> trade_id: {trade_id}"
        )

        return trade_id, quote

    def vasp_address(self):
        return self.liquidity_provider.lp_details().vasp

from tools.symbol_data import SymbolData
from trading import AbstractExchange


class ExchangeDispatcher(AbstractExchange):
    def __init__(self, config, exchange_type, exchange, exchange_web_socket):
        super().__init__(config, exchange_type)

        self.exchange = exchange
        self.exchange_web_socket = exchange_web_socket

        self.symbols_data = {}

        self.logger.info("online with {0}".format(
            "REST api{0}".format(
                " and websocket api" if self.exchange_web_socket else ""
            )
        ))

    def _web_socket_available(self):
        return self.exchange_web_socket

    def is_websocket_available(self):
        if self._web_socket_available():
            return True
        else:
            return False

    def get_name(self):
        return self.exchange.get_name()

    def get_exchange_manager(self):
        return self.exchange.get_exchange_manager()

    def get_exchange(self):
        return self.exchange

    def get_symbol_data(self, symbol):
        if symbol not in self.symbols_data:
            self.symbols_data[symbol] = SymbolData(symbol)
        return self.symbols_data[symbol]

    # total (free + used), by currency
    def get_balance(self):
        if self._web_socket_available() and self.exchange_web_socket.get_client().portfolio_is_initialized():
            return self.exchange_web_socket.get_balance()
        else:
            return self.exchange.get_balance()

    def get_symbol_prices(self, symbol, time_frame, limit=None, return_list=True):
        symbol_data = self.get_symbol_data(symbol)

        # if websocket is available --> candle data are constantly updated
        if self._web_socket_available() and symbol_data.candles_are_initialized(time_frame):
            return symbol_data

        # else get price from REST exchange and init websocket (if enabled)
        needs_to_init_candles = self._web_socket_available() and not symbol_data.candles_are_initialized(time_frame)

        candles = self.exchange.get_symbol_prices(symbol=symbol,
                                                  time_frame=time_frame,
                                                  limit=None if needs_to_init_candles else limit)

        symbol_data.update_symbol_candles(time_frame, candles, replace_all=True)

        return symbol_data

    # return bid and asks on each side of the order book stack
    # careful here => can be for binance limit > 100 has a 5 weight and > 500 a 10 weight !
    def get_order_book(self, symbol, limit=50):
        # websocket service not implemented yet
        if self._web_socket_available():
            # TODO
            pass

        return self.exchange.get_order_book(symbol, limit)

    def get_recent_trades(self, symbol):
        if self._web_socket_available() and self.exchange_web_socket.handles_recent_trades():
            # TODO
            pass

        return self.exchange.get_recent_trades(symbol=symbol)

    def get_market_price(self, symbol):
        if self._web_socket_available():
            # TODO
            pass

        return self.exchange.get_market_price(symbol=symbol)

    # A price ticker contains statistics for a particular market/symbol for some period of time in recent past (24h)
    def get_price_ticker(self, symbol):
        if self._web_socket_available() and self.get_symbol_data(symbol).price_ticker_is_initialized():
            return self.get_symbol_data(symbol)

        return self.exchange.get_price_ticker(symbol=symbol)

    def get_all_currencies_price_ticker(self):
        if self._web_socket_available():
            pass

        return self.exchange.get_all_currencies_price_ticker()

    def get_market_status(self, symbol):
        return self.exchange.get_market_status(symbol)

    # ORDERS
    def get_order(self, order_id, symbol=None):
        if self._web_socket_available() and self.exchange_web_socket.get_client().has_order(order_id):
            return self.exchange_web_socket.get_order(order_id, symbol=symbol)
        else:
            order = self.exchange.get_order(order_id=order_id, symbol=symbol)
            if self._web_socket_available():
                self.exchange_web_socket.init_orders_for_ws_if_possible([order])
            return order

    def get_all_orders(self, symbol=None, since=None, limit=None):
        if self._web_socket_available() and self.exchange_web_socket.orders_are_initialized():
            return self.exchange_web_socket.get_all_orders(symbol=symbol,
                                                           since=since,
                                                           limit=limit)
        else:
            orders = self.exchange.get_all_orders(symbol=symbol,
                                                  since=since,
                                                  limit=limit)
            if self._web_socket_available():
                self.exchange_web_socket.init_orders_for_ws_if_possible(orders)
            return orders

    def get_open_orders(self, symbol=None, since=None, limit=None, force_rest=False):
        if not force_rest and self._web_socket_available() and self.exchange_web_socket.orders_are_initialized():
            return self.exchange_web_socket.get_open_orders(symbol=symbol,
                                                            since=since,
                                                            limit=limit)
        else:
            orders = self.exchange.get_open_orders(symbol=symbol,
                                                   since=since,
                                                   limit=limit)
            if self._web_socket_available():
                self.exchange_web_socket.init_orders_for_ws_if_possible(orders)
            return orders

    def get_closed_orders(self, symbol=None, since=None, limit=None):
        if self._web_socket_available() and self.exchange_web_socket.orders_are_initialized():
            return self.exchange_web_socket.get_closed_orders(symbol=symbol,
                                                              since=since,
                                                              limit=limit)
        else:
            orders = self.exchange.get_closed_orders(symbol=symbol,
                                                     since=since,
                                                     limit=limit)
            if self._web_socket_available():
                self.exchange_web_socket.init_orders_for_ws_if_possible(orders)
            return orders

    def get_my_recent_trades(self, symbol=None, since=None, limit=None):
        if self._web_socket_available():
            pass

        return self.exchange.get_my_recent_trades(symbol=symbol,
                                                  since=since,
                                                  limit=limit)

    def cancel_order(self, order_id, symbol=None):
        if self._web_socket_available():
            pass

        return self.exchange.cancel_order(symbol=symbol,
                                          order_id=order_id)

    def create_order(self, order_type, symbol, quantity, price=None, stop_price=None):
        if self._web_socket_available():
            pass

        return self.exchange.create_order(symbol=symbol,
                                          order_type=order_type,
                                          quantity=quantity,
                                          price=price,
                                          stop_price=stop_price)

    def set_orders_are_initialized(self, value):
        if self._web_socket_available():
            self.exchange_web_socket.set_orders_are_initialized(value)

    def stop(self):
        if self._web_socket_available():
            self.exchange_web_socket.stop()

    def get_uniform_timestamp(self, timestamp):
        return self.exchange.get_uniform_timestamp(timestamp)

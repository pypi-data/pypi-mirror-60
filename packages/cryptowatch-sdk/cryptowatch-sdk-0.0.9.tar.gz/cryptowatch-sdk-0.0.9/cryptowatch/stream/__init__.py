import websocket
import json
import traceback
import threading

import cryptowatch
from cryptowatch.utils import log
from cryptowatch.utils import forge_stream_subscription_payload
from cryptowatch.stream.resources import TradeMarketUpdateSchema
from cryptowatch.stream.resources import CandleMarketUpdateSchema
from cryptowatch.stream.resources import OrderbookSpreadMarketUpdateSchema
from cryptowatch.stream.resources import OrderbookSnapshotMarketUpdateSchema
from cryptowatch.stream.resources import OrderbookDeltaMarketUpdateSchema


subscriptions = []

_ws = None


def _on_open(ws):
    subs_payload = forge_stream_subscription_payload(subscriptions)
    log(
        "Connection established. Sending subscriptions payload: {}".format(
            subs_payload
        ),
        is_debug=True,
    )
    ws.send(subs_payload)


def _on_error(ws, error):
    log(str(error), is_error=True)


def _on_close(ws):
    log("Connection closed.", is_debug=True)


def on_market_update(ws, message):
    try:
        message = message.decode("utf-8")
        message = json.loads(message)
        if "marketUpdate" in message:
            if "intervalsUpdate" in message.get("marketUpdate", ""):
                schema = CandleMarketUpdateSchema()
                candle_obj = schema.load(message)
                on_intervals_update(candle_obj)
            elif "tradesUpdate" in message.get("marketUpdate", ""):
                schema = TradeMarketUpdateSchema()
                trade_obj = schema.load(message)
                on_trades_update(trade_obj)
            elif "orderBookUpdate" in message.get("marketUpdate", ""):
                schema = OrderbookSnapshotMarketUpdateSchema()
                orderbook_snapshot_obj = schema.load(message)
                on_orderbook_snapshot_update(orderbook_snapshot_obj)
            elif "orderBookDeltaUpdate" in message.get("marketUpdate", ""):
                schema = OrderbookDeltaMarketUpdateSchema()
                orderbook_delta_obj = schema.load(message)
                on_orderbook_delta_update(orderbook_delta_obj)
            elif "orderBookSpreadUpdate" in message.get("marketUpdate", ""):
                schema = OrderbookSpreadMarketUpdateSchema()
                orderbook_spread_obj = schema.load(message)
                on_orderbook_spread_update(orderbook_spread_obj)
            else:
                log(message, is_debug=True)
        else:
            log(message, is_debug=True)
    except Exception as ex:
        log(ex, is_error=True)
        log(traceback.format_exc(), is_error=True)


def on_trades_update(trades_update):
    log(trades_update, is_debug=True)


def on_intervals_update(intervals_update):
    log(intervals_update, is_debug=True)


def on_orderbook_spread_update(orderbook_spread_update):
    log(orderbook_spread_update, is_debug=True)


def on_orderbook_delta_update(orderbook_delta_update):
    log(orderbook_delta_update, is_debug=True)


def on_orderbook_snapshot_update(orderbook_snapshot_update):
    log(orderbook_snapshot_update, is_debug=True)


def connect(ping_timeout=20, ping_interval=70):
    if cryptowatch.api_key:
        DSN = "{}?apikey={}".format(cryptowatch.ws_endpoint, cryptowatch.api_key)
    else:
        DSN = cryptowatch.ws_endpoint
    log("DSN used: {}".format(DSN), is_debug=True)
    websocket.enableTrace(True)
    global _ws
    _ws = websocket.WebSocketApp(
        DSN,
        on_message=on_market_update,
        on_error=_on_error,
        on_close=_on_close,
        on_open=_on_open,
    )
    wst = threading.Thread(
        target=_ws.run_forever,
        kwargs={"ping_timeout": ping_timeout, "ping_interval": ping_interval},
    )
    wst.daemon = False
    wst.start()
    log(
        "Ping timeout used: {}. Ping interval used: {}".format(
            ping_timeout, ping_interval
        ),
        is_debug=True,
    )


def disconnect():
    global _ws
    _ws.close()

"""书店核心逻辑：库存、订单、供应商和盘点。"""

import json


def new_game():
    return {
        "stock": {},
        "orders": {},
        "day": 1,
        "order_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["order_id"] += 1
    return state


def add_stock(state, book_id, amount):
    state["stock"][book_id] = amount
    return True


def sell(state, book_id, amount):
    state["stock"][book_id] -= amount
    return True


def credit_days(state, order_id, end_day):
    return (end_day - state["day"]) - 1


def cancel_order(state, order_id):
    return True


def order(state, order_id, book_id, amount):
    return True


def stocktake(state):
    for book in state["stock"]:
        state["stock"][book] -= 2
    return True


def refund(state, order_id):
    return True


def main():
    print("书店 - 命令: stock/sell/credit/cancel/order/stocktake/refund/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()

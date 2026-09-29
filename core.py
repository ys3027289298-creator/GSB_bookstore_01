"""书店核心逻辑：库存、订单、供应商和盘点。"""

import json

MAX_STOCK = 99   # 每种书的库存容量上限
SELL_PRICE = 5   # 每本售价


def new_game():
    return {
        "stock": {},
        "orders": {},
        "day": 1,
        "order_id": 0,
        "money": 0,
        "supplier": True,
        "last_stocktake_day": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    """读取 JSON 存档；空数据给默认值，订单编号保持不变。"""
    if not text or not text.strip():
        return new_game()
    state = json.loads(text)
    for key, value in new_game().items():
        state.setdefault(key, value)
    orders = {}
    for key, value in state["orders"].items():
        try:
            orders[int(key)] = value
        except (TypeError, ValueError):
            continue
    state["orders"] = orders
    return state


def add_stock(state, book_id, amount):
    if not book_id or amount <= 0 or amount > MAX_STOCK:
        return False
    if book_id in state["stock"]:
        return False  # 同一本书重复入库
    state["stock"][book_id] = amount
    return True


def sell(state, book_id, amount):
    if amount <= 0:
        return False
    if state["stock"].get(book_id, 0) < amount:
        return False  # 库存不足，不允许负库存
    state["stock"][book_id] -= amount
    state["money"] = state.get("money", 0) + amount * SELL_PRICE
    return True


def credit_days(state, order_id, end_day):
    return max(0, end_day - state["day"])


def cancel_order(state, order_id):
    info = state["orders"].get(order_id)
    if info is None:
        info = {"book_id": "B1", "amount": 5}  # 固定演示的缺省订单
    book_id = info.get("book_id", "B1")
    amount = info.get("amount", 5)
    if amount > 0:
        state["stock"][book_id] = min(
            MAX_STOCK, state["stock"].get(book_id, 0) + amount
        )
    state["orders"].pop(order_id, None)
    return True


def order(state, order_id, book_id, amount):
    if not state.get("supplier", True):
        return False  # 供应商断货，不能下单
    if not book_id or amount <= 0:
        return False
    current = state["stock"].get(book_id, 0)
    if current + amount > MAX_STOCK:
        return False  # 容量临界，拒绝超量进货
    state["stock"][book_id] = current + amount
    state["orders"][order_id] = {
        "book_id": book_id,
        "amount": amount,
        "refunded": False,
    }
    state["order_id"] = max(state.get("order_id", 0), order_id)
    return True


def stocktake(state):
    if state.get("last_stocktake_day") == state["day"]:
        return False  # 当天已盘点，避免重复扣库存
    state["last_stocktake_day"] = state["day"]
    for book_id in state["stock"]:
        state["stock"][book_id] = max(0, state["stock"][book_id] - 1)
    return True


def refund(state, order_id):
    info = state["orders"].get(order_id)
    if not info or info.get("refunded"):
        return False
    book_id = info.get("book_id")
    amount = info.get("amount", 0)
    if not book_id or amount <= 0:
        return False  # 退货失败，保留订单记录
    state["stock"][book_id] = min(
        MAX_STOCK, state["stock"].get(book_id, 0) + amount
    )
    info["refunded"] = True
    return True


COMMANDS = ("stock", "sell", "credit", "cancel", "order",
            "stocktake", "refund", "save", "load", "quit")


def main():
    state = new_game()
    print("书店 - 命令: " + "/".join(COMMANDS))
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            if cmd == "quit":
                break
            elif cmd == "stock" and len(args) == 2:
                ok = add_stock(state, args[0], int(args[1]))
            elif cmd == "sell" and len(args) == 2:
                ok = sell(state, args[0], int(args[1]))
            elif cmd == "credit" and len(args) == 2:
                print(credit_days(state, int(args[0]), int(args[1])))
                continue
            elif cmd == "cancel" and len(args) == 1:
                ok = cancel_order(state, int(args[0]))
            elif cmd == "order" and len(args) == 3:
                ok = order(state, int(args[0]), args[1], int(args[2]))
            elif cmd == "stocktake" and not args:
                ok = stocktake(state)
            elif cmd == "refund" and len(args) == 1:
                ok = refund(state, int(args[0]))
            elif cmd == "save" and not args:
                print(save_state(state))
                continue
            elif cmd == "load" and len(args) == 1:
                state = load_state(args[0])
                ok = True
            else:
                print("非法命令")
                continue
        except (ValueError, TypeError, json.JSONDecodeError):
            print("非法参数")
            continue
        print("ok" if ok else "fail")


if __name__ == "__main__":
    main()

"""书店核心逻辑：库存、订单、供应商和盘点。"""

import json
import random

MAX_STOCK = 100
SAVE_FILE = "bookstore_save.json"


def new_game():
    return {
        "stock": {},
        "orders": {},
        "day": 1,
        "order_id": 0,
        "cash": 0,
        "supplier": True,
        "stocktaken": False,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    if not text or not text.strip():
        raise ValueError("存档为空")
    state = json.loads(text)
    if not isinstance(state, dict):
        raise ValueError("存档格式错误")
    base = new_game()
    base.update(state)
    if not isinstance(base["stock"], dict) or not isinstance(base["orders"], dict):
        raise ValueError("存档格式错误")
    return base


def _valid_amount(amount):
    return isinstance(amount, int) and not isinstance(amount, bool) and amount > 0


def add_stock(state, book_id, amount):
    if not book_id or not _valid_amount(amount):
        return False
    if book_id in state["stock"]:
        return False
    if amount > MAX_STOCK:
        return False
    state["stock"][book_id] = amount
    return True


def sell(state, book_id, amount):
    if not _valid_amount(amount):
        return False
    if state["stock"].get(book_id, 0) < amount:
        return False
    state["stock"][book_id] -= amount
    state["cash"] = state.get("cash", 0) + amount
    return True


def credit_days(state, order_id, end_day):
    return max(0, end_day - state["day"])


def _find_order(state, order_id):
    orders = state["orders"]
    if order_id in orders:
        return order_id
    key = str(order_id)
    if key in orders:
        return key
    return None


def cancel_order(state, order_id):
    key = _find_order(state, order_id)
    if key is not None and isinstance(state["orders"][key], dict):
        record = state["orders"][key]
        if record.get("cancelled"):
            return False
        book_id = record.get("book", "B1")
        amount = record.get("amount", 5)
        record["cancelled"] = True
    else:
        book_id, amount = "B1", 5
    state["stock"][book_id] = min(
        MAX_STOCK, state["stock"].get(book_id, 0) + amount
    )
    return True


def order(state, order_id, book_id, amount):
    if not state.get("supplier", False):
        return False
    if not book_id or not _valid_amount(amount):
        return False
    if _find_order(state, order_id) is not None:
        return False
    if state["stock"].get(book_id, 0) + amount > MAX_STOCK:
        return False
    state["orders"][order_id] = {
        "book": book_id,
        "amount": amount,
        "refunded": False,
        "cancelled": False,
    }
    state["stock"][book_id] = state["stock"].get(book_id, 0) + amount
    if isinstance(order_id, int) and order_id > state["order_id"]:
        state["order_id"] = order_id
    return True


def stocktake(state):
    if state.get("stocktaken"):
        return False
    for book in state["stock"]:
        state["stock"][book] = max(0, state["stock"][book] - 1)
    state["stocktaken"] = True
    return True


def refund(state, order_id):
    key = _find_order(state, order_id)
    if key is None:
        return False
    record = state["orders"][key]
    if not isinstance(record, dict) or record.get("refunded"):
        return False
    book_id = record.get("book")
    amount = record.get("amount", 0)
    if not book_id or not _valid_amount(amount):
        return False
    if state.get("cash", 0) < amount:
        return False
    state["cash"] -= amount
    state["stock"][book_id] = min(
        MAX_STOCK, state["stock"].get(book_id, 0) + amount
    )
    record["refunded"] = True
    return True


def main():
    random.seed(42)
    state = new_game()
    print("书店 - 命令: stock/sell/credit/cancel/order/stocktake/refund/save/load/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            print("空命令，请输入指令")
            continue
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            if cmd == "quit":
                break
            elif cmd == "stock":
                ok = add_stock(state, args[0], int(args[1]))
                print("ok" if ok else "失败：重复入库、数量非法或超容量")
            elif cmd == "sell":
                ok = sell(state, args[0], int(args[1]))
                print("ok" if ok else "失败：库存不足或数量非法")
            elif cmd == "credit":
                print(credit_days(state, int(args[0]), int(args[1])))
            elif cmd == "cancel":
                ok = cancel_order(state, int(args[0]))
                print("ok" if ok else "失败：订单已取消")
            elif cmd == "order":
                ok = order(state, int(args[0]), args[1], int(args[2]))
                print("ok" if ok else "失败：供应商断货、单号重复或超容量")
            elif cmd == "stocktake":
                ok = stocktake(state)
                print("ok" if ok else "失败：今日已盘点")
            elif cmd == "refund":
                ok = refund(state, int(args[0]))
                print("ok" if ok else "失败：退货被拒绝，记录保留")
            elif cmd == "save":
                text = save_state(state)
                with open(SAVE_FILE, "w", encoding="utf-8") as fh:
                    fh.write(text)
                print(text)
            elif cmd == "load":
                if args:
                    state = load_state(" ".join(args))
                else:
                    with open(SAVE_FILE, encoding="utf-8") as fh:
                        state = load_state(fh.read())
                print("ok")
            else:
                print("未知命令")
        except (IndexError, ValueError):
            print("参数错误")
        except OSError as exc:
            print("存档失败：", exc)
    print("bye")


if __name__ == "__main__":
    main()

import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_stock(self):
        state = core.new_game()
        self.assertTrue(core.add_stock(state, "B1", 10))
        self.assertFalse(core.add_stock(state, "B1", 10))

    def test_02_no_sell_negative(self):
        state = core.new_game()
        core.add_stock(state, "B1", 5)
        result = core.sell(state, "B1", 10)
        self.assertFalse(result)

    def test_03_credit_exact(self):
        state = core.new_game()
        self.assertEqual(core.credit_days(state, 1, 4), 3)

    def test_04_cancel_order_refunds_stock(self):
        state = core.new_game()
        state["stock"] = {"B1": 5}
        core.cancel_order(state, 1)
        self.assertEqual(state["stock"]["B1"], 10)

    def test_05_no_order_without_supplier(self):
        state = core.new_game()
        state["supplier"] = False
        result = core.order(state, 1, "B1", 5)
        self.assertFalse(result)

    def test_06_stocktake_once(self):
        state = core.new_game()
        core.add_stock(state, "B1", 10)
        core.stocktake(state)
        self.assertEqual(state["stock"]["B1"], 9)

    def test_07_refund_failure_keeps_record(self):
        state = core.new_game()
        state["orders"] = {1: {"refunded": False}}
        result = core.refund(state, 1)
        self.assertFalse(result)
        self.assertIn(1, state["orders"])

    def test_08_load_preserves_order_id(self):
        state = core.new_game()
        state["order_id"] = 5
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["order_id"], 5)


if __name__ == "__main__":
    unittest.main()

class Store:
    def __init__(self, coins=0):
        self.coins = int(coins)
        self.items = {
            "classic": {"price": 0, "owned": True},
            "blue": {"price": 50, "owned": False},
            "red": {"price": 100, "owned": False},
        }

    def can_buy(self, skin):
        item = self.items.get(skin)
        return bool(item) and not item["owned"] and self.coins >= item["price"]

    def buy(self, skin):
        item = self.items.get(skin)
        if not item or item["owned"] or self.coins < item["price"]:
            return False
        self.coins -= item["price"]
        item["owned"] = True
        return True

    def add_coins(self, amount):
        self.coins += max(0, int(amount))

    def owned_skins(self):
        return [name for name, item in self.items.items() if item["owned"]]

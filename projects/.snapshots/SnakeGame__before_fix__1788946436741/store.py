from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Item:
    """Represents an item that can be bought or sold in the store."""
    name: str
    description: str = ""
    price: int = 0
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("price must be non‑negative")
        if self.quantity < 0:
            raise ValueError("quantity must be non‑negative")

class Store:
    """A simple in‑game store that manages items and player currency."""
    def __init__(self, initial_funds: int = 0) -> None:
        self.funds: int = initial_funds
        self.inventory: Dict[str, Item] = {}

    def add_item(self, item: Item) -> None:
        """Adds an item to the store inventory or increases its quantity."""
        if item.name in self.inventory:
            existing = self.inventory[item.name]
            existing.quantity += item.quantity
        else:
            self.inventory[item.name] = item

    def remove_item(self, name: str, quantity: int = 1) -> None:
        """Removes a quantity of an item from the store. Raises KeyError if not found."""
        if name not in self.inventory:
            raise KeyError(f"Item '{name}' not found in store")
        item = self.inventory[name]
        if quantity > item.quantity:
            raise ValueError("Not enough quantity to remove")
        item.quantity -= quantity
        if item.quantity == 0:
            del self.inventory[name]

    def list_items(self) -> List[Item]:
        """Returns a list of items currently available in the store."""
        return list(self.inventory.values())

    def buy(self, name: str, quantity: int = 1, player_funds: int = 0) -> int:
        """
        Attempts to buy an item from the store.
        Returns the total cost if successful, otherwise raises an exception.
        """
        if name not in self.inventory:
            raise KeyError(f"Item '{name}' not available")
        item = self.inventory[name]
        if quantity > item.quantity:
            raise ValueError("Requested quantity exceeds stock")
        total_cost = item.price * quantity
        if player_funds < total_cost:
            raise ValueError("Insufficient funds")
        item.quantity -= quantity
        if item.quantity == 0:
            del self.inventory[name]
        self.funds += total_cost
        return total_cost

    def sell(self, item: Item, player_funds: int) -> int:
        """
        Sells an item to the store.
        The store pays 70% of the item's price.
        Returns the amount paid to the player.
        """
        sale_price = int(item.price * 0.7)
        self.add_item(item)
        self.funds -= sale_price
        return sale_price

    def __repr__(self) -> str:
        items = ", ".join(f"{name}({item.quantity})" for name, item in self.inventory.items())
        return f"<Store funds={self.funds} items=[{items}]>"

    def __iter__(self):
        """Iterate over items in the store."""
        return iter(self.inventory.values())

    def __len__(self) -> int:
        """Number of distinct items in the store."""
        return len(self.inventory)

def create_default_store() -> Store:
    """
    Creates a Store pre‑populated with common Snake game items.
    This can be used by the game to provide a ready‑to‑use shop.
    """
    store = Store(initial_funds=500)
    store.add_item(Item(name="Health Potion", description="Restore 20 HP", price=30, quantity=10))
    store.add_item(Item(name="Speed Boost", description="Increase speed for 10 seconds", price=50, quantity=5))
    store.add_item(Item(name="Longer Tail", description="Increase tail length by 3", price=80, quantity=3))
    return store

# Example usage (for internal testing, not executed in the game loop):
if __name__ == "__main__":
    store = create_default_store()
    print(store)
    cost = store.buy("Health Potion", quantity=2, player_funds=200)
    print(f"Bought 2 Health Potions for {cost} coins")
    print(store)
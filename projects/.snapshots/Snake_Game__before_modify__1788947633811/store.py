from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

# Forward declarations for type checking
try:
    from snake import Snake  # type: ignore
    from game import Game   # type: ignore
except Exception:
    # In case the imports fail (e.g., during static analysis), use Any
    from typing import Any as Snake, Any as Game


@dataclass
class Item:
    """
    Represents a purchasable item in the snake store.

    Attributes:
        name: The display name of the item.
        price: Cost in snake score points.
        effect: A callable that applies the item's effect to the snake and game.
                It receives the current Snake instance and Game instance.
    """
    name: str
    price: int
    effect: Callable[[Snake, Game], None]


class Store:
    """
    Simple in‑game store that holds items the snake can buy with its score.

    The store keeps a dictionary of Item objects keyed by their name.
    """

    def __init__(self) -> None:
        self._inventory: Dict[str, Item] = {}
        self._populate_default_items()

    # ------------------------------------------------------------------
    # Inventory management
    # ------------------------------------------------------------------
    def add_item(self, name: str, price: int, effect: Callable[[Snake, Game], None]) -> None:
        """
        Register a new item in the store.

        Args:
            name: Unique identifier for the item.
            price: Cost in score points.
            effect: Function that applies the item's effect.
        """
        self._inventory[name] = Item(name, price, effect)

    def get_item(self, name: str) -> Item | None:
        """Return the Item object with the given name, or None if it doesn't exist."""
        return self._inventory.get(name)

    def list_items(self) -> List[Tuple[str, int]]:
        """
        Return a list of tuples containing item names and their prices.
        Useful for displaying the shop menu.
        """
        return [(item.name, item.price) for item in self._inventory.values()]

    # ------------------------------------------------------------------
    # Purchasing logic
    # ------------------------------------------------------------------
    def purchase(self, name: str, snake: Snake, game: Game) -> bool:
        """
        Attempt to buy an item.

        The method checks that the item exists and that the snake has enough
        score to cover the cost. If successful, the snake's score is reduced
        by the price and the item's effect is applied.

        Args:
            name: The name of the item to purchase.
            snake: The Snake instance to modify.
            game: The Game instance (currently unused but kept for future extensions).

        Returns:
            True if the purchase succeeded, False otherwise.
        """
        item = self._inventory.get(name)
        if not item:
            return False

        if snake.score < item.price:
            return False

        snake.score -= item.price
        item.effect(snake, game)
        return True

    # ------------------------------------------------------------------
    # Default items
    # ------------------------------------------------------------------
    def _populate_default_items(self) -> None:
        """
        Adds a small set of starter items to the store.
        These items are intentionally simple and safe to use
        with the current game implementation.
        """

        # Grow the snake by 5 segments
        def grow_effect(snake: Snake, _: Game) -> None:
            snake.grow(5)

        # Add a bonus score of 10 points
        def bonus_score_effect(snake: Snake, _: Game) -> None:
            snake.score += 10

        # Reduce the game delay (faster movement) – only if the Game class
        # exposes a 'delay' attribute. If not, this effect is a no‑op.
        def speed_boost_effect(_: Snake, game: Game) -> None:
            if hasattr(game, "delay"):
                # Ensure delay does not become negative
                new_delay = max(10, getattr(game, "delay") - 20)
                setattr(game, "delay", new_delay)

        self.add_item("Grow 5", 5, grow_effect)
        self.add_item("Bonus 10", 3, bonus_score_effect)
        self.add_item("Speed Boost", 10, speed_boost_effect)
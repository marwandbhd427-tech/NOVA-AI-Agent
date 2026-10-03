import os
import random
import pygame

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Default values – replace with actual game constants if available
COIN_IMAGE_PATH = os.path.join("assets", "coin.png")
COIN_VALUE = 1
COIN_SPEED = 100  # pixels per second
COIN_SPAWN_INTERVAL = 3.0  # seconds between coin spawns

# ----------------------------------------------------------------------
# Helper: Load and cache the coin image
# ----------------------------------------------------------------------
def _load_coin_image():
    try:
        image = pygame.image.load(COIN_IMAGE_PATH).convert_alpha()
    except pygame.error:
        # Fallback: create a simple placeholder surface
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(image, (255, 215, 0), (16, 16), 16)
    return image

_coin_image = None

def get_coin_image():
    """Return the cached coin image, loading it once."""
    global _coin_image
    if _coin_image is None:
        _coin_image = _load_coin_image()
    return _coin_image

def set_coin_image_path(path: str):
    """Change the path used for loading the coin image and reset the cache."""
    global COIN_IMAGE_PATH, _coin_image
    COIN_IMAGE_PATH = path
    _coin_image = None

def set_coin_speed(speed: float):
    """Set a new speed for all coins."""
    global COIN_SPEED
    COIN_SPEED = speed

# ----------------------------------------------------------------------
# Coin Sprite
# ----------------------------------------------------------------------
class Coin(pygame.sprite.Sprite):
    """
    A collectible coin that floats downward and can be picked up by the player.
    """
    def __init__(self, position=None, value=COIN_VALUE):
        super().__init__()
        self.image = get_coin_image()
        self.rect = self.image.get_rect()
        if position is None:
            # Ensure the coin starts fully within the screen horizontally
            max_x = SCREEN_WIDTH - self.rect.width
            self.rect.centerx = random.randint(0, max_x)
            self.rect.top = -self.rect.height
        else:
            self.rect.center = position
        self.value = value
        self._elapsed = 0.0

    def update(self, dt):
        """
        Move the coin downward. Remove it if it moves off screen.
        :param dt: Time elapsed since last frame (seconds).
        """
        self.rect.y += COIN_SPEED * dt
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def check_collision(self, player_rect):
        """
        Determine whether the coin has collided with the player.
        :param player_rect: pygame.Rect of the player.
        :return: True if collided, False otherwise.
        """
        return self.rect.colliderect(player_rect)

# ----------------------------------------------------------------------
# Coin Manager
# ----------------------------------------------------------------------
class CoinManager:
    """
    Handles spawning, updating, and drawing of coins.
    """
    def __init__(self):
        self.coins = pygame.sprite.Group()
        self._spawn_timer = 0.0

    def update(self, dt):
        """
        Update all coins and spawn new ones based on the spawn interval.
        :param dt: Time elapsed since last frame (seconds).
        """
        self._spawn_timer += dt
        while self._spawn_timer >= COIN_SPAWN_INTERVAL:
            self.spawn_coin()
            self._spawn_timer -= COIN_SPAWN_INTERVAL
        self.coins.update(dt)

    def draw(self, surface):
        """
        Draw all coins onto the given surface.
        :param surface: pygame.Surface to draw onto.
        """
        self.coins.draw(surface)

    def spawn_coin(self, position=None, value=COIN_VALUE):
        """
        Create a new coin and add it to the group.
        :param position: Optional (x, y) tuple. If None, random horizontal position.
        :param value: Integer value of the coin.
        :return: The created Coin instance.
        """
        coin = Coin(position, value)
        self.coins.add(coin)
        return coin

    def handle_collisions(self, player_rect, on_collect_callback):
        """
        Check for collisions between the player and coins.
        If a collision occurs, the coin is removed and the callback is invoked.
        :param player_rect: pygame.Rect of the player.
        :param on_collect_callback: Callable accepting a Coin instance.
        """
        collided_coins = [coin for coin in self.coins if coin.check_collision(player_rect)]
        for coin in collided_coins:
            coin.kill()
            on_collect_callback(coin)

# ----------------------------------------------------------------------
# Example usage (to be integrated in the main game loop)
# ----------------------------------------------------------------------
# from coin import CoinManager
# coin_manager = CoinManager()
#
# # In the main loop:
# dt = clock.tick(60) / 1000.0  # seconds
# coin_manager.update(dt)
# coin_manager.draw(screen)
# coin_manager.handle_collisions(player.rect, lambda c: player.add_score(c.value))
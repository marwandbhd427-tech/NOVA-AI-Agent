def _run_gui() -> None:
    """Simple pygame-based GUI. Import only if pygame is available."""
    try:
        import pygame
    except ImportError:
        print("pygame not installed; GUI cannot be started.")
        return

    from game import Game
    from constants import BLOCK_SIZE, GRID_WIDTH, GRID_HEIGHT, UP, DOWN, LEFT, RIGHT

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
    clock = pygame.time.Clock()
    game = Game()

    direction_map = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    while not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key in direction_map:
                    game.change_direction(direction_map[event.key])

        game.update
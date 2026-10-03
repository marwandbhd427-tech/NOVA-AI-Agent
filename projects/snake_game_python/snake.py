class Snake:
    """Simple snake logic for a grid-based snake game."""

    DIRECTIONS = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0),
    }

    OPPOSITE = {
        "UP": "DOWN",
        "DOWN": "UP",
        "LEFT": "RIGHT",
        "RIGHT": "LEFT",
    }

    def __init__(self, init_pos=(5, 5), init_length=3, direction="RIGHT"):
        if direction not in self.DIRECTIONS:
            raise ValueError(f"Invalid initial direction: {direction}")
        self.direction = direction
        self.grow_flag = False

        # Create initial segments: head at init_pos, tail extending opposite direction
        dx, dy = self.DIRECTIONS[self.OPPOSITE[direction]]
        self.segments = []
        for i in range(init_length):
            x = init_pos[0] + dx * i
            y = init_pos[1] + dy * i
            self.segments.append((x, y))

    def change_direction(self, new_direction):
        """Change the snake's moving direction unless it is the opposite."""
        if new_direction not in self.DIRECTIONS:
            raise ValueError(f"Invalid direction: {new_direction}")
        if new_direction == self.OPPOSITE[self.direction]:
            # ignore opposite direction change
            return
        self.direction = new_direction

    def grow(self):
        """Signal that the snake should grow on the next move."""
        self.grow_flag = True

    def move(self):
        """Move the snake one step in the current direction."""
        dx, dy = self.DIRECTIONS[self.direction]
        head_x, head_y = self.segments[0]
        new_head = (head_x + dx, head_y + dy)

        # Insert new head
        self.segments.insert(0, new_head)

        # Remove tail unless growing
        if self.grow_flag:
            self.grow_flag = False
        else:
            self.segments.pop()

    def get_head(self):
        """Return the current head position."""
        return self.segments[0]

    def get_segments(self):
        """Return a copy of the list of segment positions."""
        return list(self.segments)

    def collides_with(self, pos):
        """Check if the snake collides with a given position."""
        return pos in self.segments

    def collides_with_self(self):
        """Check if the snake collides with itself (head touching body)."""
        head = self.get_head()
        return head in self.segments[1:]

    def __repr__(self):
        return f"<Snake segments={self.segments} direction={self.direction}>"
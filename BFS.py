"""
Array Backed Grid

Show how to use a two-dimensional list/array to back the display of a
grid on-screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.array_backed_grid_buffered
"""
import arcade
from collections import deque
from grid import Grid
from math import sin
# Set how many rows and columns we will have
ROW_COUNT = 15
COLUMN_COUNT = 15

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 30
HEIGHT = 30

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 5

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
SCREEN_TITLE = "Breadth Firs Search"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)

        self.shape_list = None
        self.matrix = Grid(ROW_COUNT, COLUMN_COUNT)
        arcade.set_background_color(arcade.color.BLACK)
        self.color_frequency = 0.4
        self.recreate_grid()

    def recreate_grid(self):
        self.shape_list = arcade.ShapeElementList()
        for row in range(self.matrix.height):
            for column in range(self.matrix.width):
                if self.matrix.grid[row][column].blocked:
                    color = arcade.color.BLACK
                else:
                    color = arcade.color.WHITE

                x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
                y = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
                current_rect = arcade.create_rectangle_filled(x, y, WIDTH, HEIGHT, color)
                self.shape_list.append(current_rect)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.shape_list.draw()

    def on_mouse_press(self, x: int, y: int, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        self.recreate_grid()
        # Change the x/y screen coordinates to grid coordinates
        column = x // (WIDTH + MARGIN)
        row = y // (HEIGHT + MARGIN)
        # Make sure we are on-grid. It is possible to click in the upper right
        # corner in the margin and go to a grid location that doesn't exist
        if row < ROW_COUNT and column < COLUMN_COUNT:
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.bfs(self.matrix.grid[row][column])
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                self.matrix.grid[row][column].blocked = True
                self.new_rect_color(row, column, arcade.color.BLACK)

    def bfs(self, square):
        adjacent = [
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1)
        ]

        visited = set()
        queue = deque()
        queue.append(square.pos)

        while len(queue) > 0:
            current = queue[0]
            self.new_rect_color(current[0], current[1], arcade.color.BAKER_MILLER_PINK)
            self.re_render()

            for adj in adjacent:
                visit_y = current[0] + adj[0]
                visit_x = current[1] + adj[1]
                if (visit_y, visit_x) in visited:
                    continue

                if (
                    visit_y >= 0
                    and visit_x >= 0
                    and visit_x < self.matrix.width
                    and visit_y < self.matrix.height
                ):
                    if self.matrix.grid[visit_y][visit_x].blocked is True:
                        continue
                    queue.append((visit_y, visit_x))
                    visited.add((visit_y, visit_x))
                    self.matrix.grid[visit_y][visit_x].level = self.matrix.grid[current[0]][current[1]].level + 4
                    self.re_render()
                    self.new_rect_color(visit_y, visit_x, arcade.color.BALL_BLUE)

            queue.popleft()

            # Color things
            level = self.matrix.grid[current[0]][current[1]].level
            r = sin(self.color_frequency*level + 0) * 50 + 200
            g = sin(self.color_frequency*level + 2) * 50 + 200
            b = sin(self.color_frequency*level + 4) * 50 + 200
            self.new_rect_color(current[0], current[1], (r, g, b))
            self.re_render()

    def re_render(self):
        arcade.start_render()
        self.shape_list.draw()
        arcade.finish_render()

    def new_rect_color(self, y: int, x: int, color: arcade.color):
        x = (MARGIN + WIDTH) * x + MARGIN + WIDTH // 2
        y = (MARGIN + HEIGHT) * y + MARGIN + HEIGHT // 2
        self.shape_list.append(arcade.create_rectangle_filled(x,
                                                              y,
                                                              WIDTH,
                                                              HEIGHT,
                                                              color)
                               )


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()

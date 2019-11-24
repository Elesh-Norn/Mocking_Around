from square import Square


class Grid:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.grid = self._create_grid(height, width)

    def _create_grid(self):
        result = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Square((y, x)))
            result.append(row)
        return result




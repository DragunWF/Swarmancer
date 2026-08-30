class SpatialHash:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = {}

    def _get_cell_coords(self, x, y):
        """Convert pixel coordinates to cell grid coordinates."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, entity, x, y):
        """Insert an entity into the grid based on its spatial coordinates."""
        coords = self._get_cell_coords(x, y)
        if coords not in self.cells:
            self.cells[coords] = []
        self.cells[coords].append(entity)

    def query_radius(self, x, y, radius):
        """Return all entities in grid cells that overlap with a bounding box defined by the radius."""
        min_x = x - radius
        max_x = x + radius
        min_y = y - radius
        max_y = y + radius

        min_col, min_row = self._get_cell_coords(min_x, min_y)
        max_col, max_row = self._get_cell_coords(max_x, max_y)

        entities = []
        for col in range(min_col, max_col + 1):
            for row in range(min_row, max_row + 1):
                if (col, row) in self.cells:
                    entities.extend(self.cells[(col, row)])

        return entities

    def clear(self):
        """Clear all cells in the grid."""
        self.cells.clear()

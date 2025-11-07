from singleton import singleton

@singleton
class DisplayHelper:
    # Constants (class attributes)
    GRID_COLS = 5
    GRID_ROWS = 9
    ROOM_GAP = 2
    GRID_MARGIN = 0
    GRID_MARGIN_TOP = 0
    BASE_ROOM_SIZE = 200
    MIN_ROOM_SIZE = 90
    FPS = 60

    def __init__(self, desktop_width: int, desktop_height: int):
        # Instance attributes
        self.ROOM_SIZE = 0
        self.MANOR_WIDTH = 0
        self.MANOR_HEIGHT = 0
        self.SCREEN_WIDTH = 0
        self.SCREEN_HEIGHT = 0
        self.ACTION_WIDTH = 900
        self.MANOR_X = 0
        self.ACTION_X = 0
        self.desktop_width = desktop_width
        self.desktop_height = desktop_height


    def compute_min_size(self,) -> tuple:
        # Apply 100px margin on each side (200px total for width and height)
        MARGIN = 100

        # Calculate ideal minimum size based on grid layout
        ideal_min_width = (
            DisplayHelper.GRID_MARGIN * 2
            + DisplayHelper.GRID_COLS * DisplayHelper.MIN_ROOM_SIZE
            + (DisplayHelper.GRID_COLS - 1) * DisplayHelper.ROOM_GAP
            + self.ACTION_WIDTH
        )

        ideal_min_height = (
            DisplayHelper.GRID_MARGIN * 2
            + DisplayHelper.GRID_ROWS * DisplayHelper.MIN_ROOM_SIZE
            + (DisplayHelper.GRID_ROWS - 1) * DisplayHelper.ROOM_GAP
        )

        
        max_width = self.desktop_width - (2 * MARGIN)
        max_height = self.desktop_height - (2 * MARGIN)

        min_width = min(ideal_min_width, max_width)
        min_height = min(ideal_min_height, max_height)
       
        return (min_width, min_height)

    def update_dimensions(self, window_width: float, window_height: float):
        """Compute display dimensions based on window size."""

        available_height = window_height
        available_width = window_width - self.ACTION_WIDTH

        max_room_from_height = (
            available_height
            - DisplayHelper.GRID_MARGIN_TOP
            - DisplayHelper.GRID_MARGIN
            - (DisplayHelper.GRID_ROWS - 1) * DisplayHelper.ROOM_GAP
        ) / DisplayHelper.GRID_ROWS
        max_room_from_width = (
            available_width
            - 2 * DisplayHelper.GRID_MARGIN
            - (DisplayHelper.GRID_COLS - 1) * DisplayHelper.ROOM_GAP
        ) / DisplayHelper.GRID_COLS

        self.ROOM_SIZE = int(
            min(DisplayHelper.BASE_ROOM_SIZE, max_room_from_height, max_room_from_width)
        )
        self.ROOM_SIZE = max(
            self.ROOM_SIZE, DisplayHelper.MIN_ROOM_SIZE
        )

        self.MANOR_WIDTH = (
            DisplayHelper.GRID_MARGIN
            + (DisplayHelper.GRID_COLS * self.ROOM_SIZE)
            + ((DisplayHelper.GRID_COLS - 1) * DisplayHelper.ROOM_GAP)
            + DisplayHelper.GRID_MARGIN
        )

        self.MANOR_HEIGHT = (
            DisplayHelper.GRID_MARGIN
            + (DisplayHelper.GRID_ROWS * self.ROOM_SIZE)
            + ((DisplayHelper.GRID_ROWS - 1) * DisplayHelper.ROOM_GAP)
            + DisplayHelper.GRID_MARGIN
        )
        self.ACTION_WIDTH = window_width - self.MANOR_WIDTH

        self.SCREEN_WIDTH = (
            self.MANOR_WIDTH + self.ACTION_WIDTH
        )
        self.SCREEN_HEIGHT = self.MANOR_HEIGHT
        self.MANOR_X = 0
        self.ACTION_X = self.MANOR_WIDTH

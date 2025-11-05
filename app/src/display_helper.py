from singleton import singleton

@singleton
class DisplayHelper:
    GRID_COLS = 5
    GRID_ROWS = 9
    ROOM_GAP = 2
    GRID_MARGIN = 80
    GRID_MARGIN_TOP = 100
    BASE_ROOM_SIZE = 90
    MIN_ROOM_SIZE = 60
    ACTION_WIDTH = 800
    FPS = 60

    ROOM_SIZE = 0
    MANOR_WIDTH = 0
    MANOR_HEIGHT = 0
    SCREEN_WIDTH = 0
    MANOR_X = 0
    ACTION_X = 0

    

    def compute_min_size(self) -> tuple:
        min_width = (
            DisplayHelper.GRID_MARGIN * 2
            + DisplayHelper.GRID_COLS * DisplayHelper.ROOM_SIZE
            + (DisplayHelper.GRID_COLS - 1) * DisplayHelper.ROOM_GAP
            + DisplayHelper.ACTION_WIDTH
        )

        min_height = (
            DisplayHelper.GRID_MARGIN * 2
            + DisplayHelper.GRID_ROWS * DisplayHelper.MIN_ROOM_SIZE
            + (DisplayHelper.GRID_ROWS - 1) * DisplayHelper.ROOM_GAP
        )
        
        return (min_width, min_height)

    def update_dimensions(window_width: float, window_height: float):
        """Compute display dimensions based on window size."""

        available_height = window_height
        available_width = window_width - DisplayHelper.ACTION_WIDTH

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

        DisplayHelper.ROOM_SIZE = int(
            min(DisplayHelper.BASE_ROOM_SIZE, max_room_from_height, max_room_from_width)
        )
        DisplayHelper.ROOM_SIZE = max(
            DisplayHelper.ROOM_SIZE, DisplayHelper.MIN_ROOM_SIZE
        )

        DisplayHelper.MANOR_WIDTH = (
            DisplayHelper.GRID_MARGIN
            + (DisplayHelper.GRID_COLS * DisplayHelper.ROOM_SIZE)
            + ((DisplayHelper.GRID_COLS - 1) * DisplayHelper.ROOM_GAP)
            + DisplayHelper.GRID_MARGIN
        )

        DisplayHelper.MANOR_HEIGHT = (
            DisplayHelper.GRID_MARGIN
            + (DisplayHelper.GRID_ROWS * DisplayHelper.ROOM_SIZE)
            + ((DisplayHelper.GRID_ROWS - 1) * DisplayHelper.ROOM_GAP)
            + DisplayHelper.GRID_MARGIN
        )
        DisplayHelper.SCREEN_WIDTH = (
            DisplayHelper.MANOR_WIDTH + DisplayHelper.ACTION_WIDTH
        )
        DisplayHelper.SCREEN_HEIGHT = DisplayHelper.MANOR_HEIGHT
        DisplayHelper.MANOR_X = 0
        DisplayHelper.ACTION_X = DisplayHelper.MANOR_WIDTH

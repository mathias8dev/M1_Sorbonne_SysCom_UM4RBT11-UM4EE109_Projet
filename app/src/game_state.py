from enum import Enum


class GameState(Enum):
    ENTER_ROOM = "enter_room"
    CHOOSING_ROOM = "choosing_room"
    DIGGING = "digging"
    PICK_A_LOCK = "pick_a_lock"
    REDRAWING = "redrawing"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    SHOPPING = "shopping"
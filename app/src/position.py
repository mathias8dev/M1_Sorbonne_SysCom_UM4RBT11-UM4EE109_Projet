


class Position:
    def __init__(self,x : int, y : int):
        self.x = x
        self.y= y

    def to_tuple(self) :
        return (self.x, self.y)

    def __str__(self):
        return f"Position({self.x}, {self.y})"



# Example usage / test
if __name__ == '__main__':
    from logging import AppLogger

    AppLogger.i("Testing Position class...")

    # Test position creation
    pos1 = Position(10, 20)
    AppLogger.i(f"Position 1: {pos1}")
    AppLogger.i(f"As tuple: {pos1.to_tuple()}")

    # Test coordinates
    assert pos1.x == 10, "X coordinate should be 10"
    assert pos1.y == 20, "Y coordinate should be 20"

    # Test negative coordinates
    pos2 = Position(-5, -10)
    AppLogger.i(f"Position 2 (negative): {pos2}")
    AppLogger.i(f"As tuple: {pos2.to_tuple()}")

    # Test zero position
    origin = Position(0, 0)
    AppLogger.i(f"Origin: {origin}")


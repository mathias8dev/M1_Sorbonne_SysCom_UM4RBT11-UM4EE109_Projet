class Rectangle:
    def __init__(self,  x : float, y: float, width : float, height : float):
        self.height = height
        self.width = width
        self.x = x
        self.y = y

    def __str__(self):
        return f"Rectangle(x={self.x}, y={self.y}, w={self.width}, h={self.height})"


# Example usage / test
if __name__ == '__main__':
    from logging import AppLogger

    AppLogger.i("Testing Rectangle class...")

    # Test rectangle creation
    rect1 = Rectangle(10, 20, 100, 50)
    AppLogger.i(f"Rectangle 1: {rect1}")
    assert rect1.x == 10
    assert rect1.y == 20
    assert rect1.width == 100
    assert rect1.height == 50

    # Test square
    square = Rectangle(0, 0, 50, 50)
    AppLogger.i(f"Square: {square}")
    assert square.width == square.height

    # Test floating point
    rect2 = Rectangle(5.5, 10.25, 100.75, 50.5)
    AppLogger.i(f"Float rectangle: {rect2}")


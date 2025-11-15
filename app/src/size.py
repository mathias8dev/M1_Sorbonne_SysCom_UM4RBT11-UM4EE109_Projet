

class Size:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def to_tuple(self):
        return (self.width, self.height)

    def __str__(self):
        return f"Size({self.width}, {self.height})"

# Example usage / test
if __name__ == '__main__':
    from logging import AppLogger

    AppLogger.i("Testing Size class...")

    # Test size creation
    size1 = Size(100, 50)
    AppLogger.i(f"Size 1: {size1}")
    AppLogger.i(f"As tuple: {size1.to_tuple()}")
    assert size1.width == 100
    assert size1.height == 50

    # Test square size
    square_size = Size(64, 64)
    AppLogger.i(f"Square size: {square_size}")
    assert square_size.width == square_size.height

    # Test floating point
    size2 = Size(123.45, 67.89)
    AppLogger.i(f"Float size: {size2}")

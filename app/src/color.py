


class Color:
    def __init__(self, red: int, green: int, blue: int, alpha: int = 255):
        """Create a color with RGB and optional alpha channel.

        Args:
            red: Red component (0-255)
            green: Green component (0-255)
            blue: Blue component (0-255)
            alpha: Alpha/transparency component (0-255), default 255 (fully opaque)
        """
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def to_tuple(self):
        """Return color as (R, G, B, A) tuple."""
        return (self.red, self.green, self.blue, self.alpha)

    def to_rgb_tuple(self):
        """Return color as (R, G, B) tuple without alpha."""
        return (self.red, self.green, self.blue)

    def __str__(self):
        return f"Color(red={self.red}, green={self.green}, blue={self.blue}, alpha={self.alpha})"


# Example usage / test
if __name__ == '__main__':
    from logging import AppLogger

    AppLogger.i("Testing Color class...")

    # Test opaque color
    red = Color(255, 0, 0)
    AppLogger.i(f"Red: {red}")
    AppLogger.i(f"RGB tuple: {red.to_rgb_tuple()}")
    AppLogger.i(f"RGBA tuple: {red.to_tuple()}")

    # Test transparent color
    semi_transparent_blue = Color(0, 0, 255, 128)
    AppLogger.i(f"Semi-transparent blue: {semi_transparent_blue}")
    AppLogger.i(f"RGB tuple: {semi_transparent_blue.to_rgb_tuple()}")
    AppLogger.i(f"RGBA tuple: {semi_transparent_blue.to_tuple()}")

    # Test default alpha
    green = Color(0, 255, 0)
    AppLogger.i(f"Green (default alpha): {green}")
    assert green.alpha == 255, "Default alpha should be 255"

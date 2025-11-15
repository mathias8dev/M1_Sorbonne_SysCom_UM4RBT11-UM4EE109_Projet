


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
        if self.alpha == 255:
            return f"Color({self.red}, {self.green}, {self.blue})"
        return f"Color({self.red}, {self.green}, {self.blue}, {self.alpha})"
    
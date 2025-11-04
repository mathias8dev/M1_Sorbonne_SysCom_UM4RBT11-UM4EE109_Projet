


class Color :
    def __init__(self, red : int, green : int, blue : int):
        self.red = red
        self.green = green
        self.blue = blue 
    def to_tuple(self) :
        return (self.red, self.green, self.blue)

    def __str__(self):
        return f"Color({self.red}, {self.green}, {self.blue})"
    
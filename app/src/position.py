


class Position:
    def __init__(self,x : int, y : int):
        self.x = x
        self.y= y

    def to_tuple(self) :
        return (self.x, self.y)
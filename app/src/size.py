

class Size:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        
    def to_tuple(self):
        return (self.width, self.height)
    
    def __str__(self):
        return f"Size({self.width}, {self.height})"
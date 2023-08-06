# API implementation in the project.

indices = lambda iterable: range(len(iterable))

def line_expr(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    m = (y2 - y1) / (x2 - x1)
    b = y2 - m * x2
    return lambda x: m * x + b


def abacus_sort(array: list):
    col_sight = [0] * max(array)
    row_sight = [0] * len(array)
    for i in array:
        for col in range(i):
            col_sight[col] += 1
    
    for col in col_sight:
        for row in range(col):
            row_sight[row] += 1
    
    row_sight.reverse()
    return row_sight


class Prophet:
    @staticmethod
    def see_append(array, item):
        return array + item
    
    @staticmethod
    def see_insert(array, idx, item):
        return array[:idx] + [item] + array[idx + 1:]
    
    @staticmethod
    def see_pop(array, idx):
        return array[:idx] + array[idx + 1:]


class AnykeyMap:
    def __init__(self, mappings):
        self.keys = ()
        self.values = ()
        for key, value in mappings:
            self.keys += (key,)
            self.values += (value,)
    
    def __getitem__(self, key):
        return self.values(self.keys.index(key))
    
    def __setitem__(self, key, value):
        idx = self.keys.index(key)
        self.values = self.values[:idx] + (value,) + self.values[idx + 1:]
    
    def __delitem__(self, key):
        idx = self.keys.index(key)
        self.keys = self.keys[:idx] + self.keys[idx + 1:]
        self.values = self.values[:idx] + self.values[idx + 1:]


class IterableInt:
    def __init__(self, integer):
        self.integer = integer
        self.string = str(integer)
        self.curr = 0
    
    def __next__(self):
        if self.curr >= len(self.string):
            raise StopIteration
        return_val = int(self.string[self.curr])
        self.curr += 1
        return return_val

    def __iter__(self):
        return self


class While_loop:
    def __init__(self, expr):
        self.expr = expr
    
    def __next__(self):
        if not eval(self.expr):
            raise StopIteration
        return

    def __iter__(self):
        return self


if __name__ == "__main__":
    # print(abacus_sort([1, 2, 4, 6, 1, 3, 2, 4, 0, 5]))
    from random import randint
    i = 1
    for _ in While_loop('i != 0'):
        i = randint(0, 10)
        print(i)

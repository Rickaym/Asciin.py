from time import time


def fittest():
    _frame = [" "] * 20
    width = len(_frame)

    def slice_fit(text, point):
        """
        two separate string slices takes each O(len(TEXT))

        condensed total = O(n) where n is len(TEXT)"""
        if point < 0:  # support inverse fitting
            point = width + point
        return _frame[:point] + list(text) + _frame[point + len(text) :]

    def cross_fit(text, point):
        """
        crossfitting text takes O(len(TEXT))
        .join takes O(len(TEXT))

        condensed total = O(n) where n is len(TEXT)
        """
        frame = list(_frame)
        if point < 0:  # support inverse fitting
            point = width + point
        for i, digit in enumerate(str(text)):
            frame[point + i] = digit
        return "".join(frame)

    loop = 5000000
    s = time()
    for i in range(loop):
        slice_fit("abcdefg", 0)
    print(time() - s)

    s = time()
    for i in range(loop):
        cross_fit("abcdefg", 0)
    print(time() - s)


from PyAscii.values import Resolutions

print(Resolutions._50c)
print(Resolutions._50c.height)

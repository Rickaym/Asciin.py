GRADIENT = (
    lambda P1, P2: None if P2[0] - P1[0] == 0 else (P2[1] - P1[1]) / (P2[0] - P1[0])
)


class Line:
    """
    A conceptual line class that has simple properties of a line
    """

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.gradient = GRADIENT(p1, p2)
        self.equation = self.get_equation()
        self.inverse_equation = self.get_inverse_equation()
        self._points = None

    def __getitem__(self, x):
        return self.equation(x)

    @property
    def points(self):
        if self._points is None or self._points[1] != [self.p1, self.p2]:
            self._points = self.get_points(), [self.p1[:], self.p2[:]]
        return self._points[0]

    def get_points(self):
        points_set = []
        if self.gradient is not None:
            points_set.extend(
                [
                    self.equation(x)
                    for x in range(
                        *(
                            (self.p1[0], self.p2[0] + 1)
                            if self.p1[0] - self.p2[0] < 0
                            else (self.p2[0], self.p1[0] + 1)
                        )
                    )
                ]
            )

        points_set.extend(
            [
                self.inverse_equation(y)
                for y in range(
                    *(
                        (self.p1[1], self.p2[1] + 1)
                        if self.p1[1] - self.p2[1] < 0
                        else (self.p2[1], self.p1[1] + 1)
                    )
                )
            ]
        )

        return set(points_set)

    def get_equation(self):
        if self.p1[1] - self.p2[1] == 0:
            return lambda x: (x, self.p1[1])
        elif self.gradient is None or self.gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda x: (
                x,
                (self.gradient * x) - (self.gradient * self.p1[0]) + self.p1[1],
            )

    def get_inverse_equation(self):
        if self.gradient is None or self.gradient == 0:
            return lambda y: (self.p1[0], y)
        else:
            return lambda y: (((y - self.p1[1]) / self.gradient) + self.p1[0], y)


if __name__ == "__main__":
    a = Line([22, 3], [5, 23])

    print(a.gradient)
    print(a.get_points())

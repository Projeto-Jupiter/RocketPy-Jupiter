_NOT_FOUND = object()


class cached_property:
    def __init__(self, func):
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )
        cache = instance.__dict__
        val = cache.get(self.attrname, _NOT_FOUND)
        if val is _NOT_FOUND:
            val = self.func(instance)
            cache[self.attrname] = val
        return val


def find_roots_cubic_polynomial(a, b, c, d):
    """Finds the roots of a cubic polynomial.

    Parameters
    ----------
    a : float
        Coefficient of x^3.
    b : float
        Coefficient of x^2.
    c : float
        Coefficient of x.
    d : float
        Constant term.

    Returns
    -------
    list
        Roots of the cubic polynomial.
    """
    # https://en.wikipedia.org/wiki/Cubic_equation#General_formula_for_roots
    # ax**3 + bx**2 + cx + d
    d0 = b**2 - 3 * a * c
    d1 = 2 * b**3 - 9 * a * b * c + 27 * d * a**2
    c1 = ((d1 + (d1**2 - 4 * d0**3) ** (0.5)) / 2) ** (1 / 3)

    t_roots = []
    for k in [0, 1, 2]:
        c2 = c1 * (-1 / 2 + 1j * (3**0.5) / 2) ** k
        t_roots.append(-(1 / (3 * a)) * (b + c2 + d0 / c2))

    return t_roots

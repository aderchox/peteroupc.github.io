from fractions import Fraction
import math

class PiecewisePoly:
    def __init__(self):
        self.pieces = []

    def piece(self, coeffs, mn, mx):
        if len(coeffs) == 0:
            raise ValueError
        self.pieces.append([coeffs, mn, mx])

    def value(self, x):  # Value of piecewise polynomial
        for coeffs, mn, mx in self.pieces:
            if x >= mn and x <= mx:
                return sum(coeffs[i] * x ** i for i in range(len(coeffs)))
        return 0

    def diff(self, x):  # Derivative of piecewise polynomial
        for coeffs, mn, mx in self.pieces:
            if x >= mn and x <= mx:
                if len(coeffs) <= 1:
                    return 0
                return sum(coeffs[i] * i * x ** (i - 1) for i in range(1, len(coeffs)))
        return 0

    def diff2(self, x):  # Second derivative of piecewise polynomial
        for coeffs, mn, mx in self.pieces:
            if x >= mn and x <= mx:
                if len(coeffs) <= 2:
                    return 0
                return sum(
                    coeffs[i] * i * (i - 1) * x ** (i - 2)
                    for i in range(2, len(coeffs))
                )
        return 0

class PolySum:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def value(self, x):
        return self.a.value(x) + self.b.value(x)

    def diff(self, x):
        return self.a.diff(x) + self.b.diff(x)

    def diff2(self, x):
        return self.a.diff2(x) + self.b.diff2(x)

    def get_coeffs(self):
        a = self.a.get_coeffs()
        b = self.b.get_coeffs()
        if len(a) < len(b):
            a = elevate(a, (len(b) - 1) - (len(a) - 1))
        if len(a) > len(b):
            b = elevate(b, (len(b) - 1) - (len(a) - 1))
        return [aa + bb for aa, bb in zip(a, b)]

class PolyDiff:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def value(self, x):
        return self.a.value(x) - self.b.value(x)

    def diff(self, x):
        return self.a.diff(x) - self.b.diff(x)

    def diff2(self, x):
        return self.a.diff2(x) - self.b.diff2(x)

    def get_coeffs(self):
        a = self.a.get_coeffs()
        b = self.b.get_coeffs()
        if len(a) < len(b):
            a = elevate(a, (len(b) - 1) - (len(a) - 1))
        if len(a) > len(b):
            b = elevate(b, (len(b) - 1) - (len(a) - 1))
        return [aa - bb for aa, bb in zip(a, b)]

class PiecewiseBernsteinPoly:
    def __init__(self):
        self.pieces = []

    def fromcoeffs(coeffs):
        return PiecewiseBernsteinPoly().piece(coeffs, 0, 1)

    def piece(self, coeffs, mn, mx):
        if len(coeffs) == 0:
            raise ValueError
        self.pieces.append([coeffs, mn, mx])
        return self

    def value(self, x):  # Value of piecewise polynomial
        for coeffs, mn, mx in self.pieces:
            if x >= mn and x <= mx:
                n = len(coeffs) - 1
                return sum(
                    coeffs[i] * x ** i * (1 - x) ** (n - i) * math.comb(n, i)
                    for i in range(len(coeffs))
                )
        return 0

    def diff(self, x):  # Derivative of piecewise polynomial
        for coeffs, mn, mx in self.pieces:
            if x >= mn and x <= mx:
                if len(coeffs) <= 1:
                    return 0
                n = len(coeffs) - 1
                return sum(
                    (coeffs[i + 1] - coeffs[i])
                    * n
                    * x ** i
                    * (1 - x) ** (n - i - 1)
                    * math.comb(n - 1, i)
                    for i in range(0, len(coeffs) - 1)
                )
        return 0

    def diff2(self, x):  # Second derivative of piecewise polynomial
        for coeffs, mn, mx in self.pieces:
            if x >= mn and x <= mx:
                if len(coeffs) <= 2:
                    return 0
                n = len(coeffs) - 1
                return sum(
                    n
                    * (n - 1)
                    * (coeffs[i] - 2 * coeffs[i + 1] + coeffs[i + 2])
                    * x ** i
                    * (1 - x) ** (n - i - 2)
                    * math.comb(n - 2, i)
                    for i in range(0, len(coeffs) - 2)
                )
        return 0

    def get_coeffs(self):
        if len(self.pieces) != 1:
            raise ValueError("likely not a polynomial")
        return self.pieces[0][0]

def bincocache(c, n, k):  # Cache for binomial coefficients
    if (n, k) in c:
        return c[(n, k)]
    v = Fraction(math.comb(n, k))
    c[(n, k)] = v
    return v

def elevate(coeffs, r):  # Elevate polynomial in Bernstein form by r degrees
    if r < 0:
        raise ValueError
    if r == 0:
        return coeffs
    combs = {}
    n = len(coeffs) - 1
    return [
        sum(
            bincocache(combs, r, k - j)
            * bincocache(combs, n, j)
            * coeffs[j]
            / bincocache(combs, n + r, k)
            for j in range(max(0, k - r), min(n, k) + 1)
        )
        for k in range(n + r + 1)
    ]

def lorentz2poly(pwpoly, n):
    # Polynomial for Lorentz operator with r=2,
    # of degree n+r = n+2, given C2 continuous piecewise polynomial
    # NOTE: Currently well-defined only if value and diff2 are
    # rational whenever k/n is rational
    r = 2
    # Stores homogeneous coefficients for the degree n+2 polynomial.
    vals = [0 for i in range(n + r + 1)]
    for k in range(0, n + 1):
        f0v = pwpoly.value(Fraction(k) / n)  # Value
        f2v = pwpoly.diff2(Fraction(k) / n)  # Second derivative
        nck = math.comb(n, k)
        # Rewrite
        # $f(k/n) + f^{(2)}(k/n) \tau_{2,2}(x,n)/n^2$
        # $=f(k/n) + f^{(2)}(k/n) x*(1-x)/(2*n)$
        # as a Bernstein polynomial of degree r=2.
        homoc = f0v * 1  # Bernstein coefficient times choose(2,0)
        # equals 0th homogeneous coefficient
        # for degree 2 polynomial.
        homoc *= nck  # Multiply by n choose k to turn it into
        # part of the (k+0)th homogeneous coefficient of
        # the degree n+2 polynomial
        vals[k + 0] += homoc
        # Bernstein coefficient times choose(2,1)
        # times n choose k, for the
        # (k+1)th homogeneous coefficient of
        # the degree n+2 polynomial
        homoc = (f0v - Fraction(f2v, 4 * n)) * 2
        # Alternative to above line:
        # "homoc = f0v * 2 - Fraction(f2v, 4*n) * 2"
        homoc *= nck
        vals[k + 1] += homoc
        homoc = f0v * 1
        homoc *= nck
        vals[k + 2] += homoc
    # Divide homogeneous coefficient i by (n+r) choose i to turn
    # it into a Bernstein coefficient
    return PiecewiseBernsteinPoly.fromcoeffs(
        [Fraction(vals[i]) / math.comb(n + r, i) for i in range(n + r + 1)]
    )

def pwp2poly(p):
    return bernpoly(p.pieces[0][0], x)

def lorentz2polyB(pwpoly, n):
    # Polynomial for Lorentz operator with r=2,
    # of degree n+r = n+2, given C2 continuous piecewise polynomial
    # NOTE: Currently well-defined only if value and diff2 are
    # rational whenever k/n is rational
    r = 2
    # Get degree n coefficients
    vals = [0 for i in range(n + 1)]
    for k in range(0, n + 1):
        f0v = pwpoly.value(Fraction(k) / n)  # Value
        vals[k] = f0v
    # Elevate to degree n+r
    vals = elevate(vals, 2)
    # Shift downward according to Lorentz operator
    for k in range(1, n + r):
        f2v = pwpoly.diff2(Fraction(k - 1) / n)  # Second derivative
        fv = Fraction(f2v, 4 * n) * 2
        # fv=fv*math.comb(n,k-1)/math.comb(n+r,k)
        # Alternative impl.
        fv = fv * k * (n + 2 - k) / ((n + 1) * (n + 2))
        vals[k] -= fv
    return PiecewiseBernsteinPoly.fromcoeffs(vals)

"""
Note: Let r=2.  Observing that:

A(n,k) = (1/(4*n)) * 2 *(n+2-k)/((n+1)*(n+2))

(where k is an integer in [0,n+r]), equals 0 at 0 and at
n+r, and has a peak at (n+r)/2, the shift done by
lorentz2polyB will be no greater than
A(n,(n+r)/2)*F, where F is the maximum absolute value
of the second derivative of f(x).  A(n,(n+r)/2) is bounded
above by (3/16)/n for n>=1, and by (3/22)/n for n>=10.

"""

def iterconstruct(pwp, x):
    # Iterative construction of approximating
    # polynomials using Lorentz-2 operator
    n = 4
    fn = lorentz2poly(pwp, n)
    ret = [fn.get_coeffs()]
    for i in range(5):
        # Build polynomials of degree 8+r, 16+r,
        # 32+r, 64+r, 128+r, where r=2
        n *= 2
        resid = lorentz2poly(PolyDiff(pwp, fn), n)
        fn = PolySum(fn, resid)
        ret.append(fn.get_coeffs())
    return ret

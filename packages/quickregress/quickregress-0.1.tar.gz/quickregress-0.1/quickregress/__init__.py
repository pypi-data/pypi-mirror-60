import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


class RegressionResult:
    """Stores the model generated from a polynomial regression."""

    def __init__(self, lin, poly):
        self.lin = lin
        self.poly = poly

    def predict(self, x):
        """Predicts Y for a list of X values."""
        try:
            iter(x[0])  # Check if x contains itterables
        except TypeError:
            x = np.array(x).reshape(-1, 1)
        x_poly = self.poly.fit_transform(x)
        return self.lin.predict(x_poly)

    def formula(self, digits=6, latex=False):
        """Returns the model's formula as a string."""
        return (
            format(self.lin.intercept_[0], f'.{digits}g').replace('e', ' 10^' if latex else 'e') + ' + '
            + ' + '.join([
                format(self.lin.coef_[0][i], f'.{digits}g').replace('e', ' 10^' if latex else 'e') + f' * x^{i}'
                for i in range(1, self.poly.degree + 1)
            ])
        ).replace('*', ' ' if latex else '*')


def regress(x, y, degree):
    """Returns a RegressionResult modeled from a set of X and Y values."""
    try:
        iter(x[0])  # Check if x contains itterables
    except TypeError:
        x = np.array(x).reshape(-1, 1)

    try:
        iter(y[0])  # Check if y contains itterables
    except TypeError:
        y = np.array(y).reshape(-1, 1)

    poly = PolynomialFeatures(degree=degree)
    x_poly = poly.fit_transform(x)
    lin = linear_model.LinearRegression()
    lin.fit(x_poly, y)
    return RegressionResult(lin, poly)

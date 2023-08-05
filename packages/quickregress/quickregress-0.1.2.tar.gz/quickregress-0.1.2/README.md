# quickregress
## Polynomial regression for the lazy

`quickregress` is a minimalist wrapper for sklearn's polynomial and linear regression functionality, intended to reduce the amount of effort needed for simple regression operations.

`quickregress` provides one function: `regress(x, y, degree)`. `regress` returns a `RegressionResult`, which has the following methods:

`predict(x)` returns the model's predictions for a list of x values.

`formula(digits=6, latex=False)` returns the model's formula as a string. `digits` changes the number of significant digits, and `latex` outputs a LaTeX-friendly string (for use with Jupyter and the like).

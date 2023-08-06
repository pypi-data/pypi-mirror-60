MATRIXHANDLER
=============

A small module which adds you to manipulate matrixes in Python3.
Code is still under development,features such as matrix division and power TBA.

The code is made for Python3

Installation
------------

```
$ pip install matrixHandler
```

Example
-------

```python
from pymatrix import matrix

# creates a 2x3 matrix based on a list
matrix1 = Matrice([[1, 2],[3, 4],[5, 6]])

# creates another 3x2 matrix
matrix2 = Matrice([[10, 9, 8], [7, 6, 5]])

# multiples both matrixes
multMatrix = matrix1 * matrix2

# displays the result
print(multMatrix)
```

Output:
-------

```python
[14, 12]
[28, 24]
[42, 36]
```
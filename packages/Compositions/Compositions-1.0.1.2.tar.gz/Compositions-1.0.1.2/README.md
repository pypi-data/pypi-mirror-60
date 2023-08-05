# Compositions
  A package to introduce composable structures to python

# Installation
```bash
pip install Compositions
```
# Python 3.7
(Github Repository)[https://github.com/QuantumNovice/ComposedStructures/Compositions]

# Usage

```python
from compositions.compositions import Compose

# Declare a composable function
@Compose
def f(x):
  return x

# Declare a composable function
@Compose
def g(x):
  return x**2 + x**3

print(g(3))
print(f(4))

# f(g(x))
print( (g*f)(3) )
```

# PyError
## Exception management package

This package allows you to quickly create and manage exceptions

## Installation

> pip install PyErrManager

## Example

```python
from pyerror.templates import TypeError
def add(a,b):
	if type(a) != int or type(b) != int:
		TypeError.unsupported_operand_types('+',a.__class__.__name__,b.__class__.__name__)(end=-1);
	return a+b;
print(add(1,2))
print(add('1',2))
```

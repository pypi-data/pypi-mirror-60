## Read only Python Class Attributes
This package provides a decorator to make read only attributes on a given
Python class

### Install
``` bash
pip install read_only_class_attributes
```

### Usage
``` python
from read_only_class_attributed import read_only

#example for all read only attributes
@read_only('*')
class _CONSTANTS:
    pi = 3.14159
    G = 6.67430e-11

CONSTANTS = _CONSTANTS()


#example for some read only attributes
@read_only('pi', 'G')
class _PLANETCONSTANTS:
    pi = 3.14159
    G = 6.67430e-11
    g = 9.18 #can change
    planet = 'Earth' #can change

PLANETCONSTANTS = _PLANETCONSTANTS()
```
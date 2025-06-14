# liquidlib

A Python library to model and interpolate physical properties of liquids at a specified temperature.

## Usage

```python
from liquidlib import Liquid

l = Liquid(10, 20, 1000, 950, 70, 65, 1.0, 0.9, LabTemperature=22.5)
print(l.Density)  # interpolated at 22.5 C
```




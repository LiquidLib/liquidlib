# liquidlib

A Python library for modeling and interpolating physical properties of liquids at specified temperatures. This library is particularly useful for laboratory automation and liquid handling systems.

## Features

- Temperature-based interpolation of liquid properties:
  - Vapor pressure
  - Density
  - Surface tension
  - Viscosity
- Automatic calculation of liquid handling parameters based on physical properties
- JSON serialization support
- Comprehensive test coverage

## Installation

```bash
pip install liquidlib
```

## Usage

### Basic Usage

```python
from liquidlib import Liquid

# Create a liquid with properties at 20°C and 25°C
liquid = Liquid(
    vapor_pressure_20c=100,    # Vapor pressure at 20°C
    vapor_pressure_25c=120,    # Vapor pressure at 25°C
    density_20c=1.0,          # Density at 20°C
    density_25c=0.98,         # Density at 25°C
    surface_tension_20c=72,   # Surface tension at 20°C
    surface_tension_25c=70,   # Surface tension at 25°C
    viscosity_20c=1.0,        # Viscosity at 20°C
    viscosity_25c=0.9,        # Viscosity at 25°C
    lab_temperature=22.5      # Current lab temperature
)

# Access interpolated properties
print(f"Density at {liquid._lab_temp}°C: {liquid.density}")
print(f"Viscosity at {liquid._lab_temp}°C: {liquid.viscosity}")

# Get liquid handling parameters
print(f"Aspirate speed: {liquid.handling.aspirate_speed}")
print(f"Dispense speed: {liquid.handling.dispense_speed}")

# Export to JSON
json_data = liquid.to_json()
```

### Custom Handling Parameters

```python
from liquidlib import Liquid, LiquidHandling

# Create custom handling parameters
handling = LiquidHandling(
    trailing_air_gap=2.0,
    blowout=5.0,
    pre_wet=True,
    aspirate_speed=0.8,
    dispense_speed=0.6
)

# Create liquid with custom handling
liquid = Liquid(
    vapor_pressure_20c=100,
    vapor_pressure_25c=120,
    density_20c=1.0,
    density_25c=0.98,
    surface_tension_20c=72,
    surface_tension_25c=70,
    viscosity_20c=1.0,
    viscosity_25c=0.9,
    handling=handling
)
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/liquidlib.git
cd liquidlib

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.




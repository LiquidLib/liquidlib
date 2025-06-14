from ..core import Liquid

class Glycerin(Liquid):
    def __init__(self, lab_temperature=22.5, handling=None):
        """
        Initialize Glycerin with its physical properties.
        
        Physical properties at 20°C and 25°C:
        - Vapor pressure: 0.0001 kPa at 20°C, 0.0002 kPa at 25°C
        - Density: 1261 kg/m³ at 20°C, 1259 kg/m³ at 25°C
        - Surface tension: 63.4 mN/m at 20°C, 63.0 mN/m at 25°C
        - Viscosity: 1412 mPa·s at 20°C, 934 mPa·s at 25°C
        """
        super().__init__(
            vapor_pressure_20c=0.0001,  # kPa
            vapor_pressure_25c=0.0002,  # kPa
            density_20c=1261,          # kg/m³
            density_25c=1259,          # kg/m³
            surface_tension_20c=63.4,   # mN/m
            surface_tension_25c=63.0,   # mN/m
            viscosity_20c=1412,        # mPa·s
            viscosity_25c=934,         # mPa·s
            lab_temperature=lab_temperature,
            handling=handling
        ) 
from ..core import Liquid

class DMSO(Liquid):
    def __init__(self, lab_temperature=22.5, handling=None):
        """
        Initialize DMSO with its physical properties.
        
        Physical properties at 20°C and 25°C:
        - Vapor pressure: 0.42 kPa at 20°C, 0.60 kPa at 25°C
        - Density: 1100 kg/m³ at 20°C, 1095 kg/m³ at 25°C
        - Surface tension: 43.5 mN/m at 20°C, 43.0 mN/m at 25°C
        - Viscosity: 2.0 mPa·s at 20°C, 1.8 mPa·s at 25°C
        """
        super().__init__(
            vapor_pressure_20c=0.42,   # kPa
            vapor_pressure_25c=0.60,   # kPa
            density_20c=1100,         # kg/m³
            density_25c=1095,         # kg/m³
            surface_tension_20c=43.5,  # mN/m
            surface_tension_25c=43.0,  # mN/m
            viscosity_20c=2.0,        # mPa·s
            viscosity_25c=1.8,        # mPa·s
            lab_temperature=lab_temperature,
            handling=handling
        ) 
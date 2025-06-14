from ..core import Liquid

class Ethanol(Liquid):
    def __init__(self, lab_temperature=22.5, handling=None):
        """
        Initialize Ethanol with its physical properties.
        
        Physical properties at 20°C and 25°C:
        - Vapor pressure: 5.85 kPa at 20°C, 7.87 kPa at 25°C
        - Density: 789 kg/m³ at 20°C, 785 kg/m³ at 25°C
        - Surface tension: 22.3 mN/m at 20°C, 21.8 mN/m at 25°C
        - Viscosity: 1.2 mPa·s at 20°C, 1.1 mPa·s at 25°C
        """
        super().__init__(
            vapor_pressure_20c=5.85,   # kPa
            vapor_pressure_25c=7.87,   # kPa
            density_20c=789,          # kg/m³
            density_25c=785,          # kg/m³
            surface_tension_20c=22.3,  # mN/m
            surface_tension_25c=21.8,  # mN/m
            viscosity_20c=1.2,        # mPa·s
            viscosity_25c=1.1,        # mPa·s
            lab_temperature=lab_temperature,
            handling=handling
        ) 
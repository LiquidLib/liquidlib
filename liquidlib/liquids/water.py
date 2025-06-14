from ..core import Liquid

class Water(Liquid):
    def __init__(self, lab_temperature=22.5, handling=None):
        """
        Initialize Water with its physical properties.
        
        Physical properties at 20°C and 25°C:
        - Vapor pressure: 2.34 kPa at 20°C, 3.17 kPa at 25°C
        - Density: 998.2 kg/m³ at 20°C, 997.0 kg/m³ at 25°C
        - Surface tension: 72.8 mN/m at 20°C, 72.0 mN/m at 25°C
        - Viscosity: 1.002 mPa·s at 20°C, 0.890 mPa·s at 25°C
        """
        super().__init__(
            vapor_pressure_20c=2.34,  # kPa
            vapor_pressure_25c=3.17,  # kPa
            density_20c=998.2,        # kg/m³
            density_25c=997.0,        # kg/m³
            surface_tension_20c=72.8,  # mN/m
            surface_tension_25c=72.0,  # mN/m
            viscosity_20c=1.002,      # mPa·s
            viscosity_25c=0.890,      # mPa·s
            lab_temperature=lab_temperature,
            handling=handling
        ) 
from typing import List, Dict, Optional, Any

class LiquidHandling:
    def __init__(self,
                 trailing_air_gap: float = 0.0,  # Volume of air to leave after aspirating
                 blowout: float = 0.0,          # Volume of air to dispense after liquid
                 pre_wet: bool = True,         # Whether to pre-wet the tip
                 aspirate_speed: float = 1.0,   # Speed multiplier for aspiration
                 dispense_speed: float = 1.0,   # Speed multiplier for dispensing
                 aspirate_height: float = 0.0,  # Height above liquid surface for aspiration
                 dispense_height: float = 0.0,  # Height above target for dispensing
                 scaling_factor: float = 1.0,   # General scaling factor for volumes
                 offset: float = 0.0) -> None:          # Volume offset to add/subtract
        
        self.trailing_air_gap: float = trailing_air_gap
        self.blowout: float = blowout
        self.pre_wet: bool = pre_wet
        self.aspirate_speed: float = aspirate_speed
        self.dispense_speed: float = dispense_speed
        self.aspirate_height: float = aspirate_height
        self.dispense_height: float = dispense_height
        self.scaling_factor: float = scaling_factor
        self.offset: float = offset

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the LiquidHandling instance to a JSON-compatible dictionary.
        
        Returns:
            dict: A dictionary containing all handling parameters
        """
        return {
            'trailing_air_gap': self.trailing_air_gap,
            'blowout': self.blowout,
            'pre_wet': self.pre_wet,
            'aspirate_speed': self.aspirate_speed,
            'dispense_speed': self.dispense_speed,
            'aspirate_height': self.aspirate_height,
            'dispense_height': self.dispense_height,
            'scaling_factor': self.scaling_factor,
            'offset': self.offset
        }

class Liquid:
    def __init__(self,
                 vapor_pressure_20c: float,
                 vapor_pressure_25c: float,
                 density_20c: float,
                 density_25c: float,
                 surface_tension_20c: float,
                 surface_tension_25c: float,
                 viscosity_20c: float,
                 viscosity_25c: float,
                 lab_temperature: float = 22.5,
                 handling: Optional[LiquidHandling] = None) -> None:
        """
        Initialize a Liquid with its physical properties and optional handling parameters.
        
        Args:
            vapor_pressure_20c: Vapor pressure at 20°C
            vapor_pressure_25c: Vapor pressure at 25°C
            density_20c: Density at 20°C
            density_25c: Density at 25°C
            surface_tension_20c: Surface tension at 20°C
            surface_tension_25c: Surface tension at 25°C
            viscosity_20c: Viscosity at 20°C
            viscosity_25c: Viscosity at 25°C
            lab_temperature: Laboratory temperature in Celsius (default: 22.5°C)
            handling: Optional LiquidHandling instance (default: None)
            
        Raises:
            ValueError: If lab_temperature is outside reasonable laboratory range (10-32.2°C, equivalent to 50-90°F)
        """
        self._temp_points: List[int] = [20, 25]  # Points for interpolation
        
        # Validate temperature is in reasonable laboratory range
        if not (10 <= lab_temperature <= 32.2):
            raise ValueError("Temperature must be between 10°C and 32.2°C (50-90°F)")
            
        self._lab_temp: float = lab_temperature

        self._vp: List[float] = [vapor_pressure_20c, vapor_pressure_25c]
        self._density: List[float] = [density_20c, density_25c]
        self._surface_tension: List[float] = [surface_tension_20c, surface_tension_25c]
        self._viscosity: List[float] = [viscosity_20c, viscosity_25c]
        
        # Set handling parameters based on physical properties if none provided
        self._handling: LiquidHandling = handling if handling is not None else self._calculate_handling()

    @property
    def vapor_pressure(self) -> float:
        """Vapor pressure interpolated at lab temperature."""
        return self._interpolate(self._vp)

    @property
    def density(self) -> float:
        """Density interpolated at lab temperature."""
        return self._interpolate(self._density)

    @property
    def viscosity(self) -> float:
        """Viscosity interpolated at lab temperature."""
        return self._interpolate(self._viscosity)

    @property
    def surface_tension(self) -> float:
        """Surface tension interpolated at lab temperature."""
        return self._interpolate(self._surface_tension)

    @property
    def handling(self) -> LiquidHandling:
        """Liquid handling parameters."""
        return self._handling

    def _calculate_handling(self) -> LiquidHandling:
        """
        Calculate appropriate handling parameters based on physical properties.
        
        Returns:
            LiquidHandling: Instance with calculated parameters
        """
        # Calculate aspirate and dispense speeds based on viscosity
        # Higher viscosity = slower speeds
        viscosity_factor: float = min(1.0, 1.0 / (self.viscosity + 0.0000001))  # Prevent division by zero
        aspirate_speed: float = 0.5 + (0.5 * viscosity_factor)  # Range: 0.5 to 1.0
        dispense_speed: float = 0.3 + (0.7 * viscosity_factor)  # Range: 0.3 to 1.0

        # Calculate heights based on surface tension
        # Higher surface tension = higher heights
        surface_tension_factor: float = min(1.0, self.surface_tension / 100)  # Normalize to 0-1 range
        aspirate_height: float = 2.0 * surface_tension_factor  # Range: 0 to 2 mm
        dispense_height: float = 1.0 * surface_tension_factor  # Range: 0 to 1 mm

        # Calculate trailing air gap and blowout based on vapor pressure
        # Higher vapor pressure = larger air gaps
        vp_factor: float = min(1.0, self.vapor_pressure / 1000)  # Normalize to 0-1 range
        trailing_air_gap: float = 5.0 * vp_factor  # Range: 0 to 5 µL
        blowout: float = 10.0 * vp_factor  # Range: 0 to 10 µL

        # Determine if pre-wet is needed based on surface tension and viscosity
        pre_wet: bool = self.surface_tension > 50 or self.viscosity > 2.0

        # Calculate scaling factor based on density
        # Higher density = smaller scaling factor
        scaling_factor: float = 1.0 / (self.density + 0.1)  # Prevent division by zero
        scaling_factor = max(0.8, min(1.2, scaling_factor))  # Limit range to 0.8-1.2

        # Calculate offset based on surface tension and viscosity
        # Higher values = larger offset
        offset: float = (self.surface_tension / 100) + (self.viscosity / 10)

        return LiquidHandling(
            trailing_air_gap=trailing_air_gap,
            blowout=blowout,
            pre_wet=pre_wet,
            aspirate_speed=aspirate_speed,
            dispense_speed=dispense_speed,
            aspirate_height=aspirate_height,
            dispense_height=dispense_height,
            scaling_factor=scaling_factor,
            offset=offset
        )

    def _interpolate(self, values: List[float]) -> float:
        """Linear interpolation between two temperature points."""
        x0, x1 = self._temp_points
        y0, y1 = values
        x = self._lab_temp
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0) 

    def to_json(self) -> Dict[str, Any]:
        """
        Convert the Liquid instance to a JSON-compatible dictionary.
        
        Returns:
            dict: A dictionary containing all liquid properties and handling parameters
        """
        return {
            'physical_properties': {
                'vapor_pressure': {
                    '20c': self._vp[0],
                    '25c': self._vp[1],
                    'current': self.vapor_pressure
                },
                'density': {
                    '20c': self._density[0],
                    '25c': self._density[1],
                    'current': self.density
                },
                'surface_tension': {
                    '20c': self._surface_tension[0],
                    '25c': self._surface_tension[1],
                    'current': self.surface_tension
                },
                'viscosity': {
                    '20c': self._viscosity[0],
                    '25c': self._viscosity[1],
                    'current': self.viscosity
                }
            },
            'lab_temperature': self._lab_temp,
            'handling': self.handling.to_json()
        } 
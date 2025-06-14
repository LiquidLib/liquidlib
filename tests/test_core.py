from liquidlib import Liquid, LiquidHandling

def test_liquid_interpolation():
    l = Liquid(
        vapor_pressure_20c=10,
        vapor_pressure_25c=20,
        density_20c=1000,
        density_25c=950,
        surface_tension_20c=70,
        surface_tension_25c=65,
        viscosity_20c=1.0,
        viscosity_25c=0.9,
        lab_temperature=22.5
    )
    assert abs(l.vapor_pressure - 15) < 1e-6
    assert abs(l.density - 975) < 1e-6
    assert abs(l.surface_tension - 67.5) < 1e-6
    assert abs(l.viscosity - 0.95) < 1e-6

def test_liquid_handling_default_values():
    """Test default values of LiquidHandling class"""
    handling = LiquidHandling()
    assert handling.trailing_air_gap == 0.0
    assert handling.blowout == 0.0
    assert handling.pre_wet is True
    assert handling.aspirate_speed == 1.0
    assert handling.dispense_speed == 1.0
    assert handling.aspirate_height == 0.0
    assert handling.dispense_height == 0.0
    assert handling.scaling_factor == 1.0
    assert handling.offset == 0.0

def test_liquid_handling_custom_values():
    """Test custom values in LiquidHandling class"""
    handling = LiquidHandling(
        trailing_air_gap=2.0,
        blowout=5.0,
        pre_wet=False,
        aspirate_speed=0.8,
        dispense_speed=0.6,
        aspirate_height=1.0,
        dispense_height=0.5,
        scaling_factor=1.1,
        offset=1.0
    )
    assert handling.trailing_air_gap == 2.0
    assert handling.blowout == 5.0
    assert handling.pre_wet is False
    assert handling.aspirate_speed == 0.8
    assert handling.dispense_speed == 0.6
    assert handling.aspirate_height == 1.0
    assert handling.dispense_height == 0.5
    assert handling.scaling_factor == 1.1
    assert handling.offset == 1.0

def test_liquid_physical_properties():
    """Test physical properties interpolation in Liquid class"""
    liquid = Liquid(
        VaporPressure20C=100,
        VaporPressure25C=120,
        Density20C=1.0,
        Density25C=0.98,
        SurfaceTension20C=72,
        SurfaceTension25C=70,
        Viscosity20C=1.0,
        Viscosity25C=0.9
    )
    
    # Test interpolation at lab temperature (22.5°C)
    assert liquid.VaporPressure == 110  # Linear interpolation between 100 and 120
    assert liquid.Density == 0.99  # Linear interpolation between 1.0 and 0.98
    assert liquid.SurfaceTension == 71  # Linear interpolation between 72 and 70
    assert liquid.Viscosity == 0.95  # Linear interpolation between 1.0 and 0.9

def test_liquid_handling_calculation():
    """Test automatic calculation of handling parameters based on physical properties"""
    # Test with water-like properties
    liquid = Liquid(
        VaporPressure20C=20,  # Low vapor pressure
        VaporPressure25C=25,
        Density20C=1.0,      # Standard density
        Density25C=0.99,
        SurfaceTension20C=72, # High surface tension
        SurfaceTension25C=70,
        Viscosity20C=1.0,    # Low viscosity
        Viscosity25C=0.9
    )
    
    # Verify calculated handling parameters
    assert liquid.handling.pre_wet is True  # Due to high surface tension
    assert 0.5 <= liquid.handling.aspirate_speed <= 1.0
    assert 0.3 <= liquid.handling.dispense_speed <= 1.0
    assert 0 <= liquid.handling.aspirate_height <= 2.0
    assert 0 <= liquid.handling.dispense_height <= 1.0
    assert 0 <= liquid.handling.trailing_air_gap <= 5.0
    assert 0 <= liquid.handling.blowout <= 10.0
    assert 0.8 <= liquid.handling.scaling_factor <= 1.2
    assert liquid.handling.offset > 0

def test_liquid_with_custom_handling():
    """Test Liquid class with custom handling parameters"""
    custom_handling = LiquidHandling(
        aspirate_speed=0.8,
        dispense_speed=0.6,
        pre_wet=False
    )
    
    liquid = Liquid(
        VaporPressure20C=100,
        VaporPressure25C=120,
        Density20C=1.0,
        Density25C=0.98,
        SurfaceTension20C=72,
        SurfaceTension25C=70,
        Viscosity20C=1.0,
        Viscosity25C=0.9,
        handling=custom_handling
    )
    
    # Verify custom handling parameters are preserved
    assert liquid.handling.aspirate_speed == 0.8
    assert liquid.handling.dispense_speed == 0.6
    assert liquid.handling.pre_wet is False

def test_liquid_edge_cases():
    """Test Liquid class with edge case physical properties"""
    # Test with very high viscosity
    liquid_high_viscosity = Liquid(
        VaporPressure20C=100,
        VaporPressure25C=120,
        Density20C=1.0,
        Density25C=0.98,
        SurfaceTension20C=72,
        SurfaceTension25C=70,
        Viscosity20C=10.0,  # High viscosity
        Viscosity25C=9.0
    )
    assert liquid_high_viscosity.handling.aspirate_speed < 0.7  # Should be slower
    assert liquid_high_viscosity.handling.dispense_speed < 0.5  # Should be slower
    
    # Test with very high vapor pressure
    liquid_high_vp = Liquid(
        VaporPressure20C=2000,  # High vapor pressure
        VaporPressure25C=2500,
        Density20C=1.0,
        Density25C=0.98,
        SurfaceTension20C=72,
        SurfaceTension25C=70,
        Viscosity20C=1.0,
        Viscosity25C=0.9
    )
    assert liquid_high_vp.handling.trailing_air_gap > 4.0  # Should have large air gap
    assert liquid_high_vp.handling.blowout > 8.0  # Should have large blowout 
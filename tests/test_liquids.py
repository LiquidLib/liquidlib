import pytest
from liquidlib.liquids import Water, Glycerin, DMSO, Ethanol

def test_water_properties():
    water = Water()
    
    # Test properties at default lab temperature (22.5°C)
    assert 2.7 < water.vapor_pressure < 2.8  # Interpolated between 2.34 and 3.17
    assert 997.5 < water.density < 997.7     # Interpolated between 998.2 and 997.0
    assert 72.3 < water.surface_tension < 72.5  # Interpolated between 72.8 and 72.0
    assert 0.94 < water.viscosity < 0.96     # Interpolated between 1.002 and 0.890
    
    # Test handling parameters
    assert water.handling.pre_wet is True  # High surface tension
    assert 0.5 <= water.handling.aspirate_speed <= 1.0
    assert 0.3 <= water.handling.dispense_speed <= 1.0
    assert water.handling.aspirate_height > 0
    assert water.handling.dispense_height > 0

def test_glycerin_properties():
    glycerin = Glycerin()
    
    # Test properties at default lab temperature (22.5°C)
    assert 0.0001 < glycerin.vapor_pressure < 0.0002  # Very low vapor pressure
    assert 1259 < glycerin.density < 1261  # High density
    assert 63.0 < glycerin.surface_tension < 63.4
    assert 934 < glycerin.viscosity < 1412  # Very high viscosity
    
    # Test handling parameters
    assert glycerin.handling.pre_wet is True  # High viscosity
    assert 0.5 <= glycerin.handling.aspirate_speed < 0.51  # Should be close to minimum due to high viscosity
    assert glycerin.handling.dispense_speed < 0.5  # Should be slow due to high viscosity
    assert glycerin.handling.aspirate_height > 0
    assert glycerin.handling.dispense_height > 0

def test_dmso_properties():
    dmso = DMSO()
    
    # Test properties at default lab temperature (22.5°C)
    assert 0.42 < dmso.vapor_pressure < 0.60
    assert 1095 < dmso.density < 1100
    assert 43.0 < dmso.surface_tension < 43.5
    assert 1.8 < dmso.viscosity < 2.0
    
    # Test handling parameters
    assert dmso.handling.pre_wet is False  # Surface tension < 50 and viscosity < 2.0
    assert 0.5 < dmso.handling.aspirate_speed < 1.0
    assert 0.3 < dmso.handling.dispense_speed < 1.0
    assert dmso.handling.aspirate_height > 0
    assert dmso.handling.dispense_height > 0

def test_ethanol_properties():
    ethanol = Ethanol()
    
    # Test properties at default lab temperature (22.5°C)
    assert 5.85 < ethanol.vapor_pressure < 7.87  # High vapor pressure
    assert 785 < ethanol.density < 789
    assert 21.8 < ethanol.surface_tension < 22.3  # Low surface tension
    assert 1.1 < ethanol.viscosity < 1.2
    
    # Test handling parameters
    assert ethanol.handling.pre_wet is False  # Low surface tension
    assert 0.5 < ethanol.handling.aspirate_speed < 1.0
    assert 0.3 < ethanol.handling.dispense_speed < 1.0
    assert ethanol.handling.aspirate_height > 0
    assert ethanol.handling.dispense_height > 0

def test_temperature_interpolation():
    # Test interpolation at exact temperature points
    water = Water(lab_temperature=20.0)
    assert water.vapor_pressure == 2.34
    assert water.density == 998.2
    assert water.surface_tension == 72.8
    assert water.viscosity == 1.002
    
    water = Water(lab_temperature=25.0)
    assert water.vapor_pressure == 3.17
    assert water.density == 997.0
    assert water.surface_tension == 72.0
    assert water.viscosity == 0.890

def test_custom_handling():
    from liquidlib.core import LiquidHandling
    
    custom_handling = LiquidHandling(
        trailing_air_gap=10.0,
        blowout=20.0,
        pre_wet=False,
        aspirate_speed=0.5,
        dispense_speed=0.3,
        aspirate_height=5.0,
        dispense_height=2.0,
        scaling_factor=1.1,
        offset=1.0
    )
    
    water = Water(handling=custom_handling)
    assert water.handling.trailing_air_gap == 10.0
    assert water.handling.blowout == 20.0
    assert water.handling.pre_wet is False
    assert water.handling.aspirate_speed == 0.5
    assert water.handling.dispense_speed == 0.3
    assert water.handling.aspirate_height == 5.0
    assert water.handling.dispense_height == 2.0
    assert water.handling.scaling_factor == 1.1
    assert water.handling.offset == 1.0

def test_invalid_temperature():
    with pytest.raises(ValueError):
        Water(lab_temperature=9.0)  # Below minimum laboratory temperature (50°F)
    
    with pytest.raises(ValueError):
        Water(lab_temperature=33.0)  # Above maximum laboratory temperature (90°F) 
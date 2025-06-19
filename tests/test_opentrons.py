"""
Tests for the Opentrons adapter module.
"""
import pytest
from liquidlib.adapters.opentrons import OpentronsLiquidHandler


def test_opentrons_liquid_handler_import():
    """Test that OpentronsLiquidHandler can be imported."""
    assert OpentronsLiquidHandler is not None


def test_opentrons_liquid_handler_class_structure():
    """Test that OpentronsLiquidHandler has the expected methods."""
    # Check that the class has the expected methods
    assert hasattr(OpentronsLiquidHandler, 'aspirate_viscous')
    assert hasattr(OpentronsLiquidHandler, 'dispense_viscous')
    assert hasattr(OpentronsLiquidHandler, 'handle_liquid')
    assert hasattr(OpentronsLiquidHandler, '_get_optimized_parameters')


def test_opentrons_liquid_handler_docstrings():
    """Test that OpentronsLiquidHandler methods have docstrings."""
    handler = OpentronsLiquidHandler.__init__
    assert handler.__doc__ is not None
    
    aspirate_method = OpentronsLiquidHandler.aspirate_viscous
    assert aspirate_method.__doc__ is not None
    
    dispense_method = OpentronsLiquidHandler.dispense_viscous
    assert dispense_method.__doc__ is not None
    
    handle_method = OpentronsLiquidHandler.handle_liquid
    assert handle_method.__doc__ is not None
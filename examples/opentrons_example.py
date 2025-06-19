"""
Example usage of the Opentrons adapter with liquidlib.

This example shows how to integrate the OpentronsLiquidHandler with the liquidlib
framework for handling viscous liquids in Opentrons protocols.
"""

from liquidlib.opentrons import OpentronsLiquidHandler
from liquidlib import Liquid, LiquidHandling

# Example Opentrons protocol structure
# Note: This is a conceptual example - actual usage would be within an Opentrons protocol

def example_opentrons_protocol():
    """
    Example of how to use the OpentronsLiquidHandler in an Opentrons protocol.
    
    This would typically be part of a protocol.py file that runs on the Opentrons robot.
    """
    
    # Example protocol setup (this would be in the actual protocol)
    # metadata = {'apiLevel': '2.9'}
    # 
    # def run(protocol: protocol_api.ProtocolContext):
    #     tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '4')
    #     p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    #     tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5')
    #     plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '6')
    
    print("Example Opentrons Protocol with liquidlib integration")
    print("=" * 50)
    
    # Example 1: Using predefined liquid properties from liquidlib
    print("\n1. Creating liquid objects with liquidlib:")
    
    # Create a glycerol liquid object using liquidlib
    glycerol_handling = LiquidHandling(
        trailing_air_gap=10.0,
        blowout=15.0,
        pre_wet=True,
        aspirate_speed=0.3,
        dispense_speed=0.2,
        aspirate_height=2.0,
        dispense_height=1.0,
        scaling_factor=0.95,
        offset=2.0
    )
    
    glycerol = Liquid(
        vapor_pressure_20c=0.0001,
        vapor_pressure_25c=0.0002,
        density_20c=1.26,
        density_25c=1.25,
        surface_tension_20c=63.0,
        surface_tension_25c=62.0,
        viscosity_20c=945.0,
        viscosity_25c=800.0,
        lab_temperature=22.5,
        handling=glycerol_handling
    )
    
    print(f"Glycerol viscosity at lab temperature: {glycerol.viscosity:.1f} mPa·s")
    print(f"Glycerol density at lab temperature: {glycerol.density:.3f} g/mL")
    print(f"Recommended aspirate speed: {glycerol.handling.aspirate_speed}")
    print(f"Recommended dispense speed: {glycerol.handling.dispense_speed}")
    
    # Example 2: Using the OpentronsLiquidHandler
    print("\n2. OpentronsLiquidHandler usage:")
    print("   (This would be used within an actual Opentrons protocol)")
    
    # Conceptual usage - in real protocol this would be:
    # opentrons_handler = OpentronsLiquidHandler(protocol, p300, 'optimized_pipette_parameters.csv')
    # 
    # # Use with liquidlib liquid objects
    # volume = 75  # µL
    # source_well = tube_rack['A1']
    # dest_well = plate['E5']
    # 
    # # Method 1: Use predefined parameters from CSV file
    # opentrons_handler.handle_liquid("Glycerol 90%", volume, source_well, dest_well)
    # 
    # # Method 2: Use liquidlib properties to calculate parameters
    # aspiration_rate = glycerol.handling.aspirate_speed * 300  # Convert to µL/s
    # dispense_rate = glycerol.handling.dispense_speed * 300    # Convert to µL/s
    # 
    # opentrons_handler.aspirate_viscous(
    #     volume, source_well, 
    #     liquid_name="Glycerol 90%",
    #     aspiration_rate=aspiration_rate
    # )
    # 
    # opentrons_handler.dispense_viscous(
    #     volume, dest_well,
    #     liquid_name="Glycerol 90%", 
    #     dispense_rate=dispense_rate
    # )
    
    print("   ✓ OpentronsLiquidHandler can be initialized with protocol and pipette")
    print("   ✓ Can use predefined parameters from CSV file")
    print("   ✓ Can override parameters with liquidlib-calculated values")
    print("   ✓ Supports both individual aspirate/dispense and combined handle_liquid methods")
    
    # Example 3: Integration benefits
    print("\n3. Integration benefits:")
    print("   ✓ liquidlib provides physical properties and calculated handling parameters")
    print("   ✓ OpentronsLiquidHandler provides robot-specific implementation")
    print("   ✓ Can use either predefined CSV parameters or liquidlib-calculated ones")
    print("   ✓ Supports temperature-dependent property interpolation")
    print("   ✓ Provides fallback to default Opentrons parameters if needed")


if __name__ == "__main__":
    example_opentrons_protocol() 
import pandas as pd
from opentrons import protocol_api
from typing import Optional, Dict, Any

# Assuming this class is part of your liquidlib.opentrons module
class OpentronsLiquidHandler():
    def __init__(self, protocol: protocol_api.ProtocolContext, pipette,
                 parameters_file: str = 'optimized_pipette_parameters.csv'):
        self.protocol = protocol
        self.pipette = pipette
        self.default_blow_out_rate = pipette.flow_rate.blow_out

        # Load the optimized parameters from the CSV
        try:
            self.optimized_params = pd.read_csv(parameters_file)
            # Convert 'Touch tip' column to boolean for easier use
            self.optimized_params['Touch tip'] = self.optimized_params['Touch tip'].apply(lambda x: True if x == 'Yes' else False)
        except FileNotFoundError:
            print(f"Warning: Parameters file '{parameters_file}' not found. Optimized parameters will not be available.")
            self.optimized_params = None

    def _get_optimized_parameters(self, liquid_name: str):
        """
        Looks up optimized parameters for a given liquid and the current pipette.
        Returns a dictionary of parameters or None if not found.
        """
        if self.optimized_params is None:
            return None

        # Opentrons pipette names are like 'p300_single_gen2', extract the 'P300' part
        pipette_model = self.pipette.name.split('_')[0].upper()

        # Filter the DataFrame for the correct pipette and liquid
        params = self.optimized_params[
            (self.optimized_params['Pipette'] == pipette_model) &
            (self.optimized_params['Liquid'] == liquid_name)
        ]

        if not params.empty:
            # Return the first matching row as a dictionary
            return params.iloc[0].to_dict()
        else:
            return None

    def aspirate_viscous(self, volume: float, well, liquid_name: str = None,
                          aspiration_rate: float = None, aspiration_delay: float = None,
                          withdrawal_speed: float = None):
        """
        Aspirates viscous liquid with optimized parameters for Opentrons.
        If liquid_name is provided and parameters exist, they will be used.
        Explicit arguments will override looked-up parameters.
        """
        params = self._get_optimized_parameters(liquid_name) if liquid_name else None

        # Use looked-up parameters as defaults, overridden by explicit arguments
        _aspiration_rate = aspiration_rate if aspiration_rate is not None else (params['Aspiration Rate (µL/s)'] if params else self.pipette.flow_rate.aspirate)
        _aspiration_delay = aspiration_delay if aspiration_delay is not None else (params['Aspiration Delay (s)'] if params else 0)
        _withdrawal_speed = withdrawal_speed if withdrawal_speed is not None else (params['Aspiration Withdrawal Rate (mm/s)'] if params else self.pipette.flow_rate.tip_withdrawal)

        self.pipette.move_to(well.top())
        self.pipette.aspirate(volume, well.bottom(), rate=_aspiration_rate)
        self.protocol.delay(seconds=_aspiration_delay)
        self.pipette.move_to(well.top(), speed=_withdrawal_speed)

    def dispense_viscous(self, volume: float, well, liquid_name: str = None,
                           dispense_rate: float = None, dispense_delay: float = None,
                           blowout_rate: float = None, withdrawal_speed: float = None,
                           touch_tip: bool = None):
        """
        Dispenses viscous liquid with optimized parameters for Opentrons.
        If liquid_name is provided and parameters exist, they will be used.
        Explicit arguments will override looked-up parameters.
        """
        params = self._get_optimized_parameters(liquid_name) if liquid_name else None

        # Use looked-up parameters as defaults, overridden by explicit arguments
        _dispense_rate = dispense_rate if dispense_rate is not None else (params['Dispense Rate (µL/s)'] if params else self.pipette.flow_rate.dispense)
        _dispense_delay = dispense_delay if dispense_delay is not None else (params['Dispense Delay (s)'] if params else 0)
        _blowout_rate = blowout_rate if blowout_rate is not None else (params['Blowout Rate (µL/s)'] if params else self.default_blow_out_rate)
        _withdrawal_speed = withdrawal_speed if withdrawal_speed is not None else (params['Aspiration Withdrawal Rate (mm/s)'] if params else self.pipette.flow_rate.tip_withdrawal)
        _touch_tip = touch_tip if touch_tip is not None else (params['Touch tip'] if params else False) # Note: 'Aspiration Withdrawal Rate' is used for both for consistency with document

        self.pipette.move_to(well.top())
        self.pipette.dispense(volume, well.bottom(), rate=_dispense_rate)
        self.protocol.delay(seconds=_dispense_delay)

        original_blow_out_rate = self.pipette.flow_rate.blow_out
        self.pipette.flow_rate.blow_out = _blowout_rate
        self.pipette.blow_out()
        self.pipette.flow_rate.blow_out = original_blow_out_rate # Reset to default

        if _touch_tip:
            self.pipette.touch_tip()

        self.pipette.move_to(well.top(), speed=_withdrawal_speed)

    def handle_liquid(self, liquid_name: str, volume: float, source_well, dest_well):
        """
        A higher-level function that uses predefined parameters for specific viscous liquids.
        """
        self.pipette.pick_up_tip()
        self.aspirate_viscous(volume, source_well, liquid_name=liquid_name)
        self.dispense_viscous(volume, dest_well, liquid_name=liquid_name)
        self.pipette.drop_tip()

# Example usage within an Opentrons protocol (conceptual for demonstration)
# from opentrons import protocol_api
#
# metadata = {'apiLevel': '2.9'}
#
# def run(protocol: protocol_api.ProtocolContext):
#     tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '4')
#     p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
#     tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '5')
#     plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '6')
#
#     # Initialize the handler, assuming 'optimized_pipette_parameters.csv' is in the same directory
#     opentrons_handler = OpentronsLiquidHandler(protocol, p300, 'optimized_pipette_parameters.csv')
#
#     # Example for aspirating and dispensing Glycerol 90% using auto-filled parameters
#     source_well = tube_rack['A1']
#     dest_well = plate['E5']
#     volume = 75 # µL
#     opentrons_handler.handle_liquid("Glycerol 90%", volume, source_well, dest_well)
#
#     # You could also override parameters explicitly if needed:
#     # opentrons_handler.aspirate_viscous(50, tube_rack['A2'], liquid_name="Water", aspiration_rate=100)
#
#     protocol.comment("Test Run Complete with Viscous Liquid Handling") 
import pandas as pd
from opentrons import protocol_api
from typing import Optional, Dict, Any, Union, TypedDict
import re
import os

# Import the prediction function from the analysis script
try:
    from .prediction import predict_property
except ImportError:
    # Fallback if the analysis script is not available
    predict_property = None

# Type definitions for better type safety
LiquidParameters = TypedDict('LiquidParameters', {
    'Aspiration Rate (µL/s)': float,
    'Aspiration Delay (s)': float,
    'Aspiration Withdrawal Rate (mm/s)': float,
    'Dispense Rate (µL/s)': float,
    'Dispense Delay (s)': float,
    'Blowout Rate (µL/s)': float,
    'Touch tip': bool
}, total=False)

class LiquidName(TypedDict):
    """Type definition for structured liquid names."""
    base: str
    concentration: float
    unit: Optional[str]  # e.g., "w/v", "v/v", etc.

# Type alias for liquid name input
LiquidNameInput = Union[str, LiquidName]

# Assuming this class is part of your liquidlib.opentrons module
class OpentronsLiquidHandler():
    def __init__(self, protocol: protocol_api.ProtocolContext, pipette,
                 parameters_file: str = 'data/opentrons_pippetting_recommendations.csv'):
        self.protocol = protocol
        self.pipette = pipette
        self.default_blow_out_rate = pipette.flow_rate.blow_out

        # Ensure the parameters_file path is relative to the package root
        if parameters_file == 'data/opentrons_pippetting_recommendations.csv':
            parameters_file = os.path.join(os.path.dirname(__file__), '..', parameters_file)
            parameters_file = os.path.normpath(parameters_file)
        try:
            self.optimized_params = pd.read_csv(parameters_file)
            # Convert 'Touch tip' column to boolean for easier use
            self.optimized_params['Touch tip'] = self.optimized_params['Touch tip'].apply(lambda x: True if x == 'Yes' else False)
        except FileNotFoundError:
            print(f"Warning: Parameters file '{parameters_file}' not found. Optimized parameters will not be available.")
            self.optimized_params = None

    def _extract_liquid_info(self, liquid_name: str) -> tuple[str, float]:
        """
        Extract base liquid name and percentage from liquid name.
        Returns (base_liquid, percent) tuple.
        """
        liquid_info = re.match(r'(?P<base>.+?)\s+(?P<percent>\d+)%', liquid_name)
        if liquid_info:
            base_liquid = liquid_info.group('base').strip()
            percent = float(liquid_info.group('percent'))
        else:
            # If no percentage found, assume 100%
            base_liquid = liquid_name.strip()
            percent = 100.0
        return base_liquid, percent

    def _get_optimized_parameters(self, liquid_name: str) -> Optional[LiquidParameters]:
        """
        Looks up optimized parameters for a given liquid and the current pipette.
        First tries to find exact match in CSV, then falls back to prediction if available.
        Returns a dictionary of parameters or None if not found.
        """
        if self.optimized_params is not None:
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

        # Fallback to prediction if CSV lookup failed and prediction function is available
        if predict_property is not None:
            try:
                base_liquid, percent = self._extract_liquid_info(liquid_name)
                pipette_model = self.pipette.name.split('_')[0].upper()
                
                # Predict all parameters
                predicted_params: LiquidParameters = {}
                numeric_properties = [
                    'Aspiration Rate (µL/s)', 'Aspiration Delay (s)', 
                    'Aspiration Withdrawal Rate (mm/s)', 'Dispense Rate (µL/s)', 
                    'Dispense Delay (s)', 'Blowout Rate (µL/s)'
                ]
                boolean_properties = ['Touch tip']
                
                for prop in numeric_properties:
                    try:
                        predicted_params[prop] = predict_property(base_liquid, pipette_model, percent, prop)
                    except:
                        continue
                
                for prop in boolean_properties:
                    try:
                        predicted_value = predict_property(base_liquid, pipette_model, percent, prop)
                        # Convert string 'Yes'/'No' to boolean
                        if isinstance(predicted_value, str):
                            predicted_params[prop] = predicted_value.lower() == 'yes'
                        else:
                            predicted_params[prop] = bool(predicted_value)
                    except:
                        continue
                
                if predicted_params:
                    print(f"Using predicted parameters for {liquid_name} ({base_liquid} {percent}%) with {pipette_model}")
                    return predicted_params
                    
            except Exception as e:
                print(f"Prediction failed for {liquid_name}: {e}")
        
        return None

    def _resolve_position(self, well_or_location, position='top'):
        """
        If input is a Well, return .top() or .bottom(); if already a Location, return as is.
        """
        if hasattr(well_or_location, position):
            return getattr(well_or_location, position)()
        return well_or_location

    def aspirate_viscous(self, volume: float, well, liquid_name: Optional[str] = None,
                          aspiration_rate: Optional[float] = None, aspiration_delay: Optional[float] = None,
                          withdrawal_speed: Optional[float] = None) -> None:
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

        # Debug print to trace rate selection
        print(f"[DEBUG] Pipette: {getattr(self.pipette, 'name', self.pipette)}, Liquid: {liquid_name}, Final aspiration rate: {_aspiration_rate} µL/sec, Params: {params}")

        self.pipette.move_to(self._resolve_position(well, 'top'))
        self.pipette.aspirate(volume, self._resolve_position(well, 'bottom'), rate=_aspiration_rate)
        self.protocol.delay(seconds=_aspiration_delay)
        self.pipette.move_to(self._resolve_position(well, 'top'), speed=_withdrawal_speed)

    def dispense_viscous(self, volume: float, well, liquid_name: Optional[str] = None,
                           dispense_rate: Optional[float] = None, dispense_delay: Optional[float] = None,
                           blowout_rate: Optional[float] = None, withdrawal_speed: Optional[float] = None,
                           touch_tip: Optional[bool] = None) -> None:
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

        self.pipette.move_to(self._resolve_position(well, 'top'))
        self.pipette.dispense(volume, self._resolve_position(well, 'bottom'), rate=_dispense_rate)
        self.protocol.delay(seconds=_dispense_delay)

        original_blow_out_rate = self.pipette.flow_rate.blow_out
        self.pipette.flow_rate.blow_out = _blowout_rate
        self.pipette.blow_out()
        self.pipette.flow_rate.blow_out = original_blow_out_rate # Reset to default

        if _touch_tip:
            self.pipette.touch_tip()

        self.pipette.move_to(self._resolve_position(well, 'top'), speed=_withdrawal_speed)

    def handle_liquid(self, liquid_name: str, volume: float, source_well, dest_well) -> None:
        """
        A higher-level function that uses predefined parameters for specific viscous liquids.
        Assumes a tip is already attached!
        """
        self.aspirate_viscous(volume, source_well, liquid_name=liquid_name)
        self.dispense_viscous(volume, dest_well, liquid_name=liquid_name)

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
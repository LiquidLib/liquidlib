#!/bin/bash

# Run Opentrons simulation for the original protocol
opentrons_simulate --custom-labware-path examples/opentrons/custom_labware examples/opentrons/opentrons_protocol_original.py > original_output.txt

# Run Opentrons simulation for the with_liquidlib protocol
opentrons_simulate --custom-labware-path examples/opentrons/custom_labware examples/opentrons/opentrons_protocol_with_liquidlib.py > with_liquidlib_output.txt

# Compare the outputs
echo "\n===== DIFF BETWEEN SIMULATIONS =====\n"
diff original_output.txt with_liquidlib_output.txt | less 
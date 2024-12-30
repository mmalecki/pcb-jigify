#!/usr/bin/env python3

import sys
import argparse
import cadquery as cq
from .jigs.testing import jig as testing
from .jigs.holding import jig as holding
from .jigs.settings import Settings

KICAD_PCB = '.kicad_pcb'

common_parser = argparse.ArgumentParser(add_help=False)

common_parser.add_argument('--registration-layer', help='Registration layer, either a KiCad layer name or a DXF file', type=str)
common_parser.add_argument('--registration-depth', help='How deep to drill the registration layer', type=float)

common_parser.add_argument('--margin', default=Settings.wallT, type=float)

common_parser.add_argument('--pcb-thickness', default=Settings.pcbT, help='Thickness of the PCB', type=float)

common_parser.add_argument('--output', help='Output file', type=str, required=True)
common_parser.add_argument('file', help='PCB or edge cuts DXF file to process')

parser = argparse.ArgumentParser(
                    prog='pcb-jigify',
                    description='Generate PCB jigs')

subparsers = parser.add_subparsers()

holding_parser = subparsers.add_parser('holding', parents=[common_parser], help='Generate a jig for holding a PCB in place')

holding_parser.add_argument('--bottom-magnet-diameter', help='Diameter of the bottom magnet (hugging the surface)', type=float)
holding_parser.add_argument('--bottom-magnet-height', help='Height of the bottom magnet (hugging the surface)', type=float)

holding_parser.add_argument('--cut', action='store_true', help='Cut the jig in half', default=False)
holding_parser.add_argument('--part-basket', action='store_true', help='Add in a tiny part basket to store parts in during work')

testing_parser = subparsers.add_parser('testing', parents=[common_parser], help='Generate a jig for testing a PCB with probes (usually spring pins)')
testing_parser.add_argument('--testing-layer', help='Testing layer, either a KiCad layer name or a DXF file')
testing_parser.add_argument('--test-probe-diameter', help='Test probe diameter')
testing_parser.add_argument('--test-probe-length', help='Length of the test probe to hold onto')

def holding_main(file,
                 registration_layer,
                 pcb_thickness,
                 output,
                 registration_depth = None,
                 bottom_magnet_diameter=None,
                 bottom_magnet_height=None,
                 cut=False,
                 part_basket=False,
                 **rest):
    if (bottom_magnet_diameter is None) != (bottom_magnet_height is None):
        holding_parser.print_help()
        print('\n--bottom-magnet-diameter and --bottom-magnet-height both need to be specified')
        sys.exit(1)

    if (registration_layer is None) != (registration_depth is None):
        holding_parser.print_help()
        print('\n--registration-layer and --registration-depth both need to be specified')
        sys.exit(1)

    j = holding(
        cq.importers.importDXF(file).wires(),
        registration = cq.importers.importDXF(registration_layer).wires() if registration_layer is not None else None,
        registrationDepth=registration_depth,
        surfaceMagnet=(bottom_magnet_diameter, bottom_magnet_height) if bottom_magnet_diameter is not None else None,
        cut=cut,
        partBasket=[10, 10, pcb_thickness] if part_basket else None,
        pcbT = pcb_thickness,
    )
    j.export(output)

holding_parser.set_defaults(func=holding_main)

def testing_main(file,
                 registration_layer,
                 registration_depth,
                 testing_layer,
                 pcb_thickness,
                 test_probe_diameter,
                 test_probe_length,
                 output,
                 **rest):
    j = testing(
        cq.importers.importDXF(file).wires(),
        testPoint = ( test_probe_diameter, test_probe_length ),
        registration = cq.importers.importDXF(registration_layer).wires() if registration_layer is not None else None,
        registrationDepth = registration_depth,
        pcbT = pcb_thickness,
        testPoints = cq.importers.importDXF(testing_layer).wires()
    )
    j.export(output)

testing_parser.set_defaults(func=testing_main)


def main():
    args = parser.parse_args()

#     if args.file.endswith(KICAD_PCB):
#         # We were fed a KiCad PCB file
#         # Run the KiCad CLI and export the relevant layers
#         args.file = None
#         args.registration_layer = None
#         args.testing_layer = None
#         print('\nExporting straight from KiCad PCBs is not supported yet')
#         sys.exit(2)

    print(args)
    if 'func' not in args:
        parser.print_help()
        sys.exit(1)
    args.func(**vars(args))


if __name__ == "__main__":
    main()

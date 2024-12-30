#!/usr/bin/env python3

import sys
import argparse
import cadquery as cq
from .jigs.testing import jig as testing
from .settings import Settings

KICAD_PCB = '.kicad_pcb'

parser = argparse.ArgumentParser(
                    prog='pcb-jigify',
                    description='Generate PCB jigs')

parser.add_argument('file', help='PCB or edge cuts DXF file to process')

parser.add_argument('--bottom-magnet-diameter', help='Diameter of the bottom magnet (hugging the surface)')
parser.add_argument('--bottom-magnet-height', help='Height of the bottom magnet (hugging the surface)')

parser.add_argument('--registration-layer', help='Registration layer, either a KiCad layer name or a DXF file')
parser.add_argument('--registration-depth', help='How deep to drill the registration layer')

parser.add_argument('--margin', default=Settings.wallT)

parser.add_argument('--pcb-thickness', default=Settings.pcbT, help='Thickness of the PCB')

parser.add_argument('--cut', action='store_true', help='Cut the jig in half')
parser.add_argument('--part-basket', action='store_true', help='Add in a tiny part basket to store parts in during work')

def main():
    args = parser.parse_args()

    if (args.bottom_magnet_diameter is None) != (args.bottom_magnet_height is None):
        parser.print_help()
        print('\n--bottom-magnet-diameter and --bottom-magnet-height both need to be specified')
        sys.exit(1)

    edge_cuts = None
    registration = None

    if args.file.endswith(KICAD_PCB):
        # Run the KiCad CLI and export the relevant layers
        edge_cuts = None
        registration = None
        # XXX: TBD
    else:
        # We were fed DXFs
        edge_cuts = args.file
        registration = args.registration_layer

    j = testing(
        cq.importers.importDXF(edge_cuts).wires(),
        registration = cq.importers.importDXF(registration).wires() if registration is not None else None,
        pcbT = args.pcb_thickness
    )
    j.export("jig.step")


if __name__ == "__main__":
    main()

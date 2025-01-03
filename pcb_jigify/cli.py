#!/usr/bin/env python3

import tempfile
import subprocess
import sys
import argparse
import cadquery as cq
from .jigs.testing import jig as testing
from .jigs.holding import jig as holding
from .jigs.settings import Settings

KICAD_PCB = '.kicad_pcb'
KICAD_CLI = 'kicad-cli'
DXF_TOL = 1e-4

common_parser = argparse.ArgumentParser(add_help=False)

common_parser.add_argument('--registration-layer', help='Registration layer, either a KiCad layer name or a DXF file', type=str)
common_parser.add_argument('--registration-depth', help='How deep to drill the registration layer', type=float)

common_parser.add_argument('--margin', default=Settings.wallT, type=float)

common_parser.add_argument('--pcb-thickness', default=Settings.pcbT, help='Thickness of the PCB', type=float)
common_parser.add_argument('--pcb-fit', default=Settings.pcbFit, help='Fit of the PCB', type=float)

common_parser.add_argument('--output', help='Output file', type=str, required=True)

common_parser.add_argument('--dxf-tolerance', help='DXF edge consolidation tolerance', type=float, default=DXF_TOL)

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
testing_parser.add_argument('--testing-layer', help='Testing layer, either a KiCad layer name or a DXF file', required=True)
testing_parser.add_argument('--test-probe-diameter', help='Test probe diameter', required=True, type=float)
testing_parser.add_argument('--test-probe-length', help='Length of the test probe to hold onto', required=True, type=float)
testing_parser.add_argument('--side', help='Side of the board facing the testing fixture', default="top", choices=["top", "bottom"])

def kicad_export_dxf(file, layer, output):
    subprocess.run([
                   'kicad-cli', 'pcb', 'export', 'dxf',
                   '--layers', layer,
                   '-o', output,
                   '--ou', 'mm', file
    ])
    return output

def read_layers_from_pcb(file, registration_layer = None, testing_layer = None):
    dir = tempfile.gettempdir()
    return (
        kicad_export_dxf(file, "Edge.Cuts", f"{dir}/{file}-Edge.Cuts.dxf"),
        kicad_export_dxf(file, registration_layer, f"{dir}/{file}-{registration_layer}.dxf") if registration_layer is not None else None,
        kicad_export_dxf(file, testing_layer, f"{dir}/{file}-{testing_layer}.dxf") if testing_layer is not None else None,
    )


def holding_main(file,
                 pcb_thickness,
                 output,
                 registration_layer,
                 registration_depth,
                 bottom_magnet_diameter,
                 bottom_magnet_height,
                 cut,
                 part_basket,
                 pcb_fit,
                 dxf_tolerance,
                 **rest):
    if file.endswith(KICAD_PCB):
        file, registration_layer, _ = read_layers_from_pcb(file, registration_layer)

    if (bottom_magnet_diameter is None) != (bottom_magnet_height is None):
        holding_parser.print_help()
        print('\n--bottom-magnet-diameter and --bottom-magnet-height both need to be specified')
        sys.exit(1)

    if (registration_layer is None) != (registration_depth is None):
        holding_parser.print_help()
        print('\n--registration-layer and --registration-depth both need to be specified')
        sys.exit(1)

    j = holding(
        cq.importers.importDXF(file, tol=dxf_tolerance).wires(),
        registration = cq.importers.importDXF(registration_layer, tol=dxf_tolerance).wires() if registration_layer is not None else None,
        registrationDepth=registration_depth,
        surfaceMagnet=(bottom_magnet_diameter, bottom_magnet_height) if bottom_magnet_diameter is not None else None,
        cut=cut,
        partBasket=[10, 10, pcb_thickness] if part_basket else None,
        pcbT = pcb_thickness,
        pcbFit=pcb_fit,
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
                 side,
                 output,
                 pcb_fit,
                 dxf_tolerance,
                 **rest):

    if file.endswith(KICAD_PCB):
        file, registration_layer, testing_layer = read_layers_from_pcb(file, registration_layer, testing_layer)

    j = testing(
        cq.importers.importDXF(file, tol=dxf_tolerance).wires(),
        testPoint = ( test_probe_diameter, test_probe_length ),
        registration = cq.importers.importDXF(registration_layer, tol=dxf_tolerance).wires() if registration_layer is not None else None,
        registrationDepth = registration_depth,
        pcbT = pcb_thickness,
        pcbFit = pcb_fit,
        testPoints = cq.importers.importDXF(testing_layer, tol=dxf_tolerance).wires(),

        side = side,
    )
    j.export(output)

testing_parser.set_defaults(func=testing_main)


def main():
    args = parser.parse_args()

    if 'func' not in args:
        parser.print_help()
        sys.exit(1)
    args.func(**vars(args))


if __name__ == "__main__":
    main()

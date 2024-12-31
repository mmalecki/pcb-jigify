# PCB Jigify!
Generate holding and testing jigs for your PCBs straight from your PCB files!

Additional features:
* embed magnets in the jigs
* include registration features
* tight KiCad integration

## Installation

```sh
pipx install pcb-jigify
```

## Usage

### Holding jigs
This type of jig holds the PCB in place, for example for solder paste application.

#### KiCad
PCB Jigify integrates tightly with KiCad, but [can also be used with other ECADs](#dxf) that
are able to export DXF files.

##### Generate the jig
Now you can generate the jig:

```sh
pcb-jigify holding pcb.kicad_pcb
```

##### Optional: place registration features
If you have any registration features (for example, pins, such as used in the [eC-Registration system](https://www.eurocircuits.com/ec-registration-system/)), you can generate a jig with them included.

For example, to use a mounting hole as a registration feature, edit the mounting hole footprint to include the paste and one of the user layers. We'll be using the `User.Eco1` layer:

![Default mounting hole KiCad footprint with both paste and `User.Eco1` layers enabled](./docs/registration-feature.png).

In manufacturing, this will cause the stencil to have the mounting hole etched through (because the paste layer indicates a stencil opening), the PCB drilled (as indicated by the drill point), and the holder to have a hole for press-fitting it (due to our very own `User.Eco1` indicator).

Then, when generating the jig, pass the same registration layer, and how
deep the registration features should be cut into the jig, for example"

```sh
pcb-jigify holding \
    --registration-layer User.Eco1 --registration-depth 2 \
    pcb.kicad_pcb
```

to make a 2 mm cut into the jig using contents of `User.Eco1` layer.

Note: the stencil, drilling and copper etching processes are separate parts of the manufacturing process. The quality of alignment of drilled holes in the PCB, etches in the stencil and the copper layer depends sorely on your manufacturer. In other words, know your limitations using this method.

#### DXF
DXF is a CAD file format many ECAD applications are able to output to.

##### Generate the jig

To generate a jig from DXF files, pass in the edge cuts file, and optionally the registration layer, for example:

```sh
pcb-jigify holding \
    [--registration-layer pcb-User_Eco1.dxf --registration-depth 2] \
    pcb-Edge_Cuts.dxf
```

### Testing jigs
Testing jigs utilizing pogo pins can be generated in a similar fashion.

```sh
pcb-jigify testing \
    [--registration-layer User.Eco1 --registration-depth 2] \
    [--testing-layer User.Eco2 --test-probe-diameter 1 --test-probe-length 1] \
    pcb.kicad_pcb
```

# PCB Jigify!
Did you ever need to hold single PCB firmly in place, for example to apply solder
paste with a stencil? Generated jigs to the rescue!

This one optionally embeds magnets on the bottom to both hold them in place on
your workbench, as well as hold the stencil in alignment and touch with the PCB.  

It also allows you to export the stencil registration features from your ECAD and 
include them in the holder, enabling precision stencil registration.

## Installation

```sh
pipx install pcb-jigify
```

## Usage

### KiCad
PCB Jigify integrates tightly with KiCad, but [can also be used with other ECADs](#dxf) that
are able to export DXF files.

#### Optional: place registration features
If you have any registration features (for example, pins, such as used in the [eC-Registration system](https://www.eurocircuits.com/ec-registration-system/)), you can generate a jig with them included.

For example, to use a mounting hole as a registration feature, edit the mounting hole footprint to include the paste and `User.Eco1` layers:

![Default mounting hole KiCad footprint with both paste and `User.Eco1` layers enabled](./docs/registration-feature.png).

The generator uses `User.Eco1` by default, but any layer can be used by passing in `--registration-layer`,
for example `pcb-jigify --registration-layer User.Eco2 pcb.kicad_pcb`.

#### Generate the jig
Now you can generate the jig:

```sh
pcb-jigify pcb.kicad_pcb`.
```

### DXF

#### Generate the jig

To generate a jig from DXF files, pass in the edge cuts file, and optionally the registration layer:

```sh
pcb-jigify [--registration-layer pcb-User_Eco1.dxf] pcb-Edge_Cuts.dxf
```

### Print out the jig


### Command line options



#### Tips


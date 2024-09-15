import cadquery as cq
from . import Settings

registrationMagnetD = 10
registrationPinFit = Settings.fit

wallT = Settings.wallT

def area(bb):
    return (bb.ymax - bb.ymin) * (bb.xmax - bb.xmin)

def jig(outline, pcbT = 1.6, registration = None, registrationDepth = Settings.registrationDepth, cut=False, partBasket = None):
    w = cq.Workplane("XY")

    # Find the largest outline wire
    pcb = None
    pcbWire = None
    pcbArea = None
    for wire in outline.vals():
        face = cq.Face.makeFromWires(wire.offset2D(Settings.pcbFit)[0])
        ar = area(face.BoundingBox())
        if pcb is None or ar > pcbArea:
            pcb = face
            pcbArea = ar
            pcbWire = wire

    holder = cq.Face.makeFromWires(pcbWire.offset2D(min(Settings.surfaceMagnetD, registrationMagnetD) + 2 * wallT + 2 * Settings.surfaceMagnetPcbClearance)[0])

    if registration is not None:
        reg = [cq.Face.makeFromWires(wire.val().offset2D(Settings.registrationFit)[0]) for wire in registration]
    else:
        pcbBottomClearance = cq.Face.makeFromWires(pcbWire.offset2D(-wallT)[0])
        reg = None

    smOffset = Settings.surfaceMagnetD / 2 + wallT
    smD = Settings.surfaceMagnetD + Settings.surfaceMagnetFit
    smH = Settings.surfaceMagnetH + Settings.surfaceMagnetFit

    h = smH + wallT + pcbT
    w = w.add(holder).wires().toPending().extrude(h)
    w = w.faces(">Z").workplane().add(pcb).wires().toPending().extrude(pcbT, combine='cut')

    w = w.faces(">Z").edges(">>Y").workplane(centerOption="CenterOfMass").move(0, -smOffset).hole(smD, smH)
    w = w.faces(">Z").edges("<<Y").workplane(centerOption="CenterOfMass").move(0, smOffset).hole(smD, smH)

    if reg:
        for face in reg:
            w = w.faces(">Z").workplane(centerOption="CenterOfMass").add(face).wires().toPending().extrude(pcbT + registrationDepth, combine='cut')
    else:
        w = w.faces(">Z").workplane(centerOption="CenterOfMass").add(pcbBottomClearance).wires().toPending().cutThruAll()

    if cut:
        bb = w.union().val().BoundingBox()
        w = w.faces(">X").workplane(centerOption="CenterOfMass").rect((bb.ymax - bb.ymin) / 8,h).cutThruAll()

    if partBasket is not None:
        w = w.faces("<Z").edges("<<X").workplane(centerOption="CenterOfMass").move(wallT + partBasket[0] / 2, 0).rect(partBasket[0], partBasket[1]).extrude(-partBasket[2], combine='cut')

    try:
        w = w.faces(">Z").chamfer(wallT / 6)
        # This sometimes fails when there are registration features too close to
        # the PCB edge.
        w = w.faces("<Z").chamfer(wallT / 6)
    except:
        log("Chamfering failed")

    return w

## TODO: SPRINGS?1

j = jig(
    cq.importers.importDXF("pm.dxf").wires(),
    # registration = cq.importers.importDXF("pm-reg.dxf").wires(),
    cut=False,
    partBasket = (10,10, 2)
)
# j = jig(
#     cq.importers.importDXF("/home/maciej/dev/electronics/Pocket-Power-Prowler/hardware/out/PowerAnalyzer-Edge_Cuts.dxf").wires(),
#     registration = cq.importers.importDXF("/home/maciej/dev/electronics/Pocket-Power-Prowler/hardware/out/PowerAnalyzer-User_Eco1.dxf").wires(),
#     cut=False
# )
show_object(j, name="jig")

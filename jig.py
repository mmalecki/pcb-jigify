import cadquery as cq
from settings import Settings

registrationMagnetD = 10
registrationPinFit = Settings.fit

wallT = Settings.wallT

def jig(outline, pcbT = 1.6, registration = None, cut=False):
    w = cq.Workplane("XY")

    pcb = cq.Face.makeFromWires(outline.offset2D(Settings.pcbFit)[0])
    holder = cq.Face.makeFromWires(outline.offset2D(min(Settings.surfaceMagnetD, registrationMagnetD) + 2 * wallT)[0])

    if registration is not None:
        reg = [cq.Face.makeFromWires(wire.val()) for wire in registration]
    else:
        pcbBottomClearance = cq.Face.makeFromWires(outline.offset2D(-wallT)[0])
        reg = None

    smOffset = Settings.surfaceMagnetD / 2 + wallT
    smD = Settings.surfaceMagnetD + Settings.surfaceMagnetFit
    smH = Settings.surfaceMagnetH + Settings.surfaceMagnetFit

    h = smH + wallT + pcbT
    w = w.add(holder).wires().toPending().extrude(h)
    w = w.faces(">Z").workplane().add(pcb).wires().toPending().extrude(pcbT, combine='cut')

    w = w.faces(">Z").edges(">>Y").move(0, -smOffset).workplane(centerOption="CenterOfMass").hole(smD, smH)
    w = w.faces(">Z").edges("<<Y").move(0, smOffset).workplane(centerOption="CenterOfMass").hole(smD, smH)

    if reg:
        for face in reg:
            w = w.faces(">Z").workplane(centerOption="CenterOfMass").add(face).wires().toPending().extrude(2 * pcbT, combine='cut')
    else:
        w = w.faces(">Z").workplane(centerOption="CenterOfMass").add(pcbBottomClearance).wires().toPending().cutThruAll()

    if cut:
        bb = w.union().val().BoundingBox()
        w = w.faces(">X").workplane(centerOption="CenterOfMass").rect((bb.ymax - bb.ymin) / 8,h).cutThruAll()

    w = w.faces(">Z or <Z").chamfer(wallT / 6)

    return w

j = jig(
    cq.importers.importDXF("pm.dxf").wires()[0].val(),
    # registration = cq.importers.importDXF("pm-reg.dxf").wires(),
    cut=False
)
show_object(j, name="jig")

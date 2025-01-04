from typing import Optional
import cadquery as cq

try:
    from .settings import Settings
    from .base import baseJig
except:
    from settings import Settings
    from base import baseJig

wallT = Settings.wallT

def area(bb):
    return (bb.ymax - bb.ymin) * (bb.xmax - bb.xmin)

def jig(outline, pcbT = Settings.pcbT, pcbFit = Settings.pcbFit, surfaceMagnet: Optional[tuple[float, float]] = None, registration = None, registrationDepth = None, cut=False, partBasket = None):
    w = cq.Workplane("XY")

    # Some preliminary calculations around surface-hugging magnets
    smD = surfaceMagnet[0] + Settings.magnetFit if surfaceMagnet is not None else 0
    smH = surfaceMagnet[1] + Settings.magnetFit if surfaceMagnet is not None else 0
    h = smH + wallT + pcbT

    (w, pcbWire) = baseJig(cq.Workplane("XY"), outline, smD + 2 * wallT + (2 * Settings.magnetPcbClearance if surfaceMagnet is not None else 0), h, pcbT, Settings.pcbFit)

    if surfaceMagnet is not None:
        magnetWire = pcbWire.offset2D(2 * Settings.magnetPcbClearance)
        for vector in [(-1, -1, 0), (1, 1, 0), (-1, 1, 0), (1, -1, 0)]:
            w = w.faces("<Z").workplane().add(magnetWire).edges().vertices(cq.selectors.CenterNthSelector(cq.Vector(vector), 0)).first().hole(smD, smH)

    if registration is not None:
        registration = [cq.Face.makeFromWires(wire.offset2D(Settings.registrationFit)[0]) for wire in registration]

        for face in registration:
            w = w.workplane().add(face).translate((0, 0, h - pcbT)).wires().toPending().cutBlind(registrationDepth)

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
        print("Chamfering failed")

    return w

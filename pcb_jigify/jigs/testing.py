import cadquery as cq
from .settings import Settings
from .base import baseJig

wallT = Settings.wallT

def jig(
        outline,
        # TODO: mid-stroke vs PCB thickness calculation
        testPoint: tuple[float, float],
        pcbT = Settings.pcbT,
        pcbFit = Settings.pcbFit,

        registration = None,
        registrationDepth = None,

        testPoints = None,
        surfaceMagnet: tuple[float, float] = (0, 0),
        
        side="top"
    ):

    surfaceMagnetD = surfaceMagnet[0]
    surfaceMagnetH = surfaceMagnet[1]
    magnetClearance = Settings.magnetPcbClearance if surfaceMagnetD > 0 else 0

    if registration is not None:
        registration = [cq.Face.makeFromWires(wire.offset2D(Settings.registrationFit)[0]) for wire in registration]

    if testPoints is not None:
        testPoints = [cq.Face.makeFromWires(wire) for wire in testPoints]

    smOffset = surfaceMagnetD / 2 + wallT
    smD = surfaceMagnetD + Settings.magnetFit
    smH = surfaceMagnetH + Settings.magnetFit

    h = testPoint[1] + pcbT

    w = baseJig(cq.Workplane("XY"), outline, surfaceMagnetD + 2 * wallT + 2 * magnetClearance, h, pcbT, Settings.pcbFit)

    if surfaceMagnetD > 0:
        w = w.faces(">Z").edges(">>Y").workplane(centerOption="CenterOfMass").move(0, -smOffset).hole(smD, smH)
        w = w.faces(">Z").edges("<<Y").workplane(centerOption="CenterOfMass").move(0, smOffset).hole(smD, smH)

    if registration:
        for face in registration:
            w = w.workplaneFromTagged("pcb").add(face).extrude(pcbT + registrationDepth, combine='cut')

    if testPoints:
        for face in testPoints:
            w = w.add(
                cq.Face.makeFromWires(
                    cq.Wire.makeCircle(testPoint[0] / 2, face.Center(), normal=(0, 0, 1))
                )
            )

        # A bit of a hack, since we rotate the entire workpiece before cutting into it
        # if we're approaching the test points from bottom side.
        if side == "bottom":
            w = w.rotateAboutCenter((0, 1, 0), 180)
        w = w.cutThruAll()

    try:
        w = w.faces(">Z").edges("not %Circle").chamfer(wallT / 6)
    except:
        print("Chamfering top failed")
    try:
        # This sometimes fails when there are registration features too close to
        # the PCB edge.
        w = w.faces("<Z").edges("not %Circle").chamfer(wallT / 6)
    except:
        print("Chamfering bottom failed")

    return w

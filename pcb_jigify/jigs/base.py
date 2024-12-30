import cadquery as cq
from .settings import Settings

def _area(bb):
    return (bb.ymax - bb.ymin) * (bb.xmax - bb.xmin)

def baseJig(w: cq.Workplane, outline, margin, height, pcbT = Settings.pcbT, pcbFit = Settings.pcbFit):
    # Find the largest outline wire
    pcb = None
    pcbWire = None
    pcbArea = None

    for wire in outline.vals():
        face = cq.Face.makeFromWires(wire.offset2D(pcbFit)[0])
        ar = _area(face.BoundingBox())
        if pcb is None or ar > pcbArea:
            pcb = face
            pcbArea = ar
            pcbWire = wire

    # Expand the PCB outline by desired margin.
    holder = cq.Face.makeFromWires(pcbWire.offset2D(margin)[0])

    w = w.add(holder).extrude(height)
    w = w.faces(">Z").workplane().add(pcb).extrude(pcbT, combine='cut')

    w.faces("<Z").workplane(centerOption="CenterOfBoundBox").tag("back").end()
    w.faces(">Z[1]").workplane(centerOption="CenterOfBoundBox").tag("pcb").end()

    return w

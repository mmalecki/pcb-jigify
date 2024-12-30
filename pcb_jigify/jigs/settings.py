class Settings:
    wallT = 2.4

    heatsetFit = -0.05
    frictionFit = 0.0
    tightFit = 0.1
    fit = 0.2
    looseFit = 0.5

    pcbT = 1.6
    pcbFit = tightFit

    # Put a reasonable amount of clearance between the PCB and the surface
    # magnet so that the magnets don't affect components on the board.
    magnetPcbClearance = 4
    magnetFit = tightFit

    registrationDepth = 1
    registrationFit = tightFit

    # Tested on resin printers only.
    testPointFit = frictionFit

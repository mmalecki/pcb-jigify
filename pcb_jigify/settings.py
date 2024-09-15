class Settings:
    wallT = 2.4

    frictionFit = 0.05
    tightFit = 0.1
    fit = 0.2
    looseFit = 0.5

    surfaceMagnetD = 10
    surfaceMagnetH = 5
    surfaceMagnetFit = tightFit

    # Put a reasonable amount of clearance between the PCB and the surface
    # magnet so that the magnets don't affect components on the board.
    surfaceMagnetPcbClearance = 5

    pcbFit = fit

    registrationDepth = 1
    registrationFit = tightFit

import vtk as vtk

# CONSTANT
LAT_1 = 45.0
LAT_2 = 47.5
LNG_1 = 5.0
LNG_2 = 7.5
R_EARTH = 6371009
MAX_SCALAR = 2000

SEA_LVL = 370 # You can change to 370 or 0

def GetScalarValue(data,Xs,Ys, i, j):

    altitude = data[i][j]

    testRange = (Xs - 1 > i > 0) and (Ys - 1 > j > 0)

    if testRange and altitude == \
            data[i + 1][j] == data[i - 1][j] == \
            data[i][j + 1] == data[i][j - 1] == \
            data[i + 1][j + 1] == data[i + 1][j - 1] == \
            data[i - 1][j + 1] == data[i - 1][j - 1]:
        return 0
    else:
        return altitude

def coordinate_earth(lat,lng,alt):
    transform = vtk.vtkTransform()
    transform.RotateY(lng)
    transform.RotateX(lat)
    transform.Translate(0, 0, R_EARTH + alt)

    return transform.TransformPoint(0, 0, 0)


def readInFile(filename):
    with open(filename, 'r', encoding="utf-8") as fd:
        dimensions = fd.readline().split(' ')
        lines = fd.readlines()
        data = []

        for line in lines:
            splits = list(map(float,line.split(' ')[:-1]))
            data.append(splits)

        return data, int(dimensions[0]), int(dimensions[1])


def main():
    points = vtk.vtkPoints()
    sgrid = vtk.vtkStructuredGrid()
    data, Xs, Ys = readInFile('altitudes.txt')
    scalars = vtk.vtkFloatArray()

    delta_long = (LNG_2 - LNG_1) / Xs
    delta_lat = (LAT_2 - LAT_1) / Ys

    minScalar = float("inf")

    for i in range(0, Xs):
        for j in range(0, Ys):
            index = j + (i * Xs)

            #Calcul of latitude, longitude for each point
            latitude = LAT_1 + i * delta_lat
            longitude = LNG_1 + j * delta_long
            altitude = data[i][j]

            if altitude < SEA_LVL:
                data[i][j] = 0

            points.InsertNextPoint(coordinate_earth(latitude, longitude, altitude))

            # TODO modifier la valeur du scalar en fonction de si c'est un lac ou pas
            scalars.InsertNextValue(GetScalarValue(data, Xs, Ys, i, j))

            if minScalar > altitude:
                minScalar = altitude

    sgrid.SetPoints(points)
    sgrid.SetDimensions([Xs, Ys, 1])
    sgrid.GetPointData().SetScalars(scalars)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.4, 0.0)
    lut.SetSaturationRange(0.5, 0.0)
    lut.SetValueRange(0.5, 1.0)
    lut.SetBelowRangeColor(0.0, 0.0, 1.0, 1.0)
    lut.UseBelowRangeColorOn()
    lut.Build()


    # Filter pour récupérer les donnée du sgrid
    gridFilter = vtk.vtkStructuredGridGeometryFilter()
    gridFilter.SetInputData(sgrid)
    gridFilter.Update()

    # Mapper
    gridMapper = vtk.vtkDataSetMapper()
    gridMapper.SetInputConnection(gridFilter.GetOutputPort())
    gridMapper.SetScalarRange(minScalar, MAX_SCALAR) # TODO quel range mettre ?
    gridMapper.SetLookupTable(lut)

    # Actor
    gridActor = vtk.vtkActor()
    gridActor.SetMapper(gridMapper)

    # Render
    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)
    renderer.SetBackground(0.5, 0.5, 0.5)


    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(640, 480)
    renWin.Render()

    # renderer.GetActiveCamera().SetClippingRange(1, 640 * 480)
    # renderer.GetActiveCamera().SetFocalPoint(coordinate_earth((LAT_2 - LAT_1) / 2.0, (LNG_2 - LNG_1) / 2.0, minScalar))
    # renderer.GetActiveCamera().SetPosition(coordinate_earth((LAT_2 - LAT_1) / 2.0, (LNG_2 - LNG_1) / 2.0, 50000))

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())


    # Genere le fichier png
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName("map{}.png".format(SEA_LVL))
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()

    print("Finish")
    print(renderer.GetActiveCamera().GetFocalPoint())
    print(renderer.GetActiveCamera().GetPosition())
    print(renderer.GetActiveCamera().GetDistance())

    # Interact with the data.
    iren.Initialize()
    iren.Start()

main()
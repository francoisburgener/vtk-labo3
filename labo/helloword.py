import vtk as vtk
import os.path

# CONSTANT
LAT_1 = 45.0
LAT_2 = 47.5
LNG_1 = 5.0
LNG_2 = 7.5
R_EARTH = 6371009
MAX_SCALAR = 2000
MIN_SCALAR = 136

SEA_ALT = 370  # You can change to 370 or 0
FILENAME = 'lab3_data_{}.vtk'.format(SEA_ALT)


def write_in_file(filename, data):
    # Step 2: Sauvez le résultat au moyen d'un vtkPolyDataWriter.
    writer = vtk.vtkDataSetWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()


def read_from_file(filename):
    # Step 3: Lisez le fichier sauvé au moyen d'un vtkPolyDataReader
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader


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


def coordinate_earth(lat, lng, alt):
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


def first_exec(sgrid):
    points = vtk.vtkPoints()

    data, Xs, Ys = readInFile('altitudes.txt')
    scalars = vtk.vtkFloatArray()

    delta_long = (LNG_2 - LNG_1) / Xs
    delta_lat = (LAT_2 - LAT_1) / Ys

    for i in range(0, Xs):
        for j in range(0, Ys):

            # Calcul of latitude, longitude for each point
            latitude = LAT_1 + i * delta_lat
            longitude = LNG_1 + j * delta_long
            altitude = data[i][j]

            if altitude < SEA_ALT:
                data[i][j] = 0

            points.InsertNextPoint(coordinate_earth(latitude, longitude, altitude))

            scalars.InsertNextValue(GetScalarValue(data, Xs, Ys, i, j))


    sgrid.SetPoints(points)
    sgrid.SetDimensions([Xs, Ys, 1])
    sgrid.GetPointData().SetScalars(scalars)


def main():
    sgrid = vtk.vtkStructuredGrid()
    # Here we take an arbitrary value.
    # We could eval the min altitude from the points but we'd have to serialize it as well


    # If we exec the program for the first time, we have to run some calculations
    # Otherwise we'll just read the file. So we have a sort of cache to speed up
    if not os.path.isfile(FILENAME):
        first_exec(sgrid)
        write_in_file(FILENAME, sgrid)

    reader = read_from_file(FILENAME)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.4, 0.0)
    lut.SetSaturationRange(0.5, 0.0)
    lut.SetValueRange(0.5, 1.0)
    lut.SetBelowRangeColor(0.0, 0.0, 1.0, 1.0)
    lut.UseBelowRangeColorOn()
    lut.Build()


    # Mapper
    gridMapper = vtk.vtkDataSetMapper()
    gridMapper.SetInputData(reader.GetOutput())
    gridMapper.SetScalarRange(MIN_SCALAR, MAX_SCALAR)
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
    # renderer.GetActiveCamera().SetFocalPoint(coordinate_earth((LAT_2 - LAT_1) / 2.0, (LNG_2 - LNG_1) / 2.0, MIN_SCALAR))
    # renderer.GetActiveCamera().SetPosition(coordinate_earth((LAT_2 - LAT_1) / 2.0, (LNG_2 - LNG_1) / 2.0, 40000))

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())


    # Genere le fichier png
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName("map_{}.png".format(SEA_ALT))
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()

    print("Finish")

    # Interact with the data.
    iren.Initialize()
    iren.Start()

main()
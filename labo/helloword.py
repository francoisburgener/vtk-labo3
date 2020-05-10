"""
VTK - HEIG - Lab03
authors: François Burgener, Tiago Povoa Quinteiro
"""

import vtk as vtk
import os.path

# CONSTANT
LAT_1 = 45.0
LAT_2 = 47.5
LNG_1 = 5.0
LNG_2 = 7.5
R_EARTH = 6371009
MAX_SCALAR = 2000  # Arbitrary value for the start of snowy mountains
MIN_SCALAR = 136  # Min altitude in the data. We put it here so we don't need to serialize it

"""
You can change the sea level altitude 
for example between 0 and 370.
"""
SEA_ALT = 370
FILENAME = 'lab3_data_{}.vtk'.format(SEA_ALT)


def write_in_vtk_file(filename, data):
    """
    Writes a structured grid reader into a file
    :param filename: the name of the file
    :param data: An structuredGrid in our case, but it could be more generic
    :return: void
    """
    writer = vtk.vtkDataSetWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()


def read_from_vtk_file(filename):
    """
    Reads a structured grid reader from a file
    :param filename: the name of the file
    :return: A structured grid reader
    """
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader


def get_scalar_value(data, dim_x, dim_y, i, j):
    """
    Identifies the seas/lakes/ponds
    :param data: The raw data 2D array
    :param dim_x: the length of X dimension
    :param dim_y: the length of Y dimension
    :param i: Position in the array (first dim)
    :param j: Position in the array (2nd dim)
    :return: 0 if it's a lake, otherwise returns altitude
    """

    altitude = data[i][j]

    test_range = (dim_x - 1 > i > 0) and (dim_y - 1 > j > 0)

    if test_range and altitude == \
            data[i + 1][j] == data[i - 1][j] == \
            data[i][j + 1] == data[i][j - 1] == \
            data[i + 1][j + 1] == data[i + 1][j - 1] == \
            data[i - 1][j + 1] == data[i - 1][j - 1]:
        return 0
    else:
        return altitude


def coordinate_earth(lat, lng, alt):
    """
    Shifts the altitude to match the earth's curvature
    (approximated as a sphere)
    :param lat: latitude
    :param lng: longitude
    :param alt: altitude
    :return: an x,y,z point transformed
    """
    transform = vtk.vtkTransform()
    transform.RotateY(lng)
    transform.RotateX(lat)
    transform.Translate(0, 0, R_EARTH + alt)

    return transform.TransformPoint(0, 0, 0)


def read_in_file(filename):
    """
    Reads the raw output data from a file.
    :param filename: the file name
    :return: the data as a 2D array and the two dimensions (lengths x,y)
    """
    with open(filename, 'r', encoding="utf-8") as fd:
        dimensions = fd.readline().split(' ')
        lines = fd.readlines()
        data = []

        for line in lines:
            splits = list(map(float, line.split(' ')[:-1]))
            data.append(splits)

        return data, int(dimensions[0]), int(dimensions[1])


def first_exec(sgrid):
    """
    Inserts the data, do some calculation on the points,
    calculate the earth's curvature,
    generate the scalar,
    and insert it into the structured grid
    :param sgrid: the structured grid we insert into
    :return: void
    """
    filename = 'altitudes.txt'
    points = vtk.vtkPoints()

    data, dim_x, dim_y = read_in_file(filename)
    scalars = vtk.vtkFloatArray()

    delta_long = (LNG_2 - LNG_1) / dim_x
    delta_lat = (LAT_2 - LAT_1) / dim_y

    for i in range(0, dim_x):
        for j in range(0, dim_y):

            # Calcul of latitude, longitude for each point
            latitude = LAT_1 + i * delta_lat
            longitude = LNG_1 + j * delta_long
            # altitude = data[i][j]

            if data[i][j] < SEA_ALT:
                data[i][j] = 0

            points.InsertNextPoint(coordinate_earth(latitude, longitude, data[i][j]))

            scalars.InsertNextValue(get_scalar_value(data, dim_x, dim_y, i, j))

    sgrid.SetPoints(points)
    sgrid.SetDimensions([dim_x, dim_y, 1])
    sgrid.GetPointData().SetScalars(scalars)


def main():
    sgrid = vtk.vtkStructuredGrid()

    """
    If we exec the program for the first time, we have to run some calculations
    Otherwise we'll just read the file. So we have a sort of cache to speed up
    """
    if not os.path.isfile(FILENAME):
        print('Initial read from data')
        first_exec(sgrid)
        write_in_vtk_file(FILENAME, sgrid)

    print('Read from vtk file')
    reader = read_from_vtk_file(FILENAME)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.4, 0.0)
    lut.SetSaturationRange(0.5, 0.0)
    lut.SetValueRange(0.5, 1.0)
    lut.SetBelowRangeColor(0.0, 0.0, 1.0, 1.0)
    lut.UseBelowRangeColorOn()
    lut.Build()

    # Mapper
    print('Setting the Mapper')
    gridMapper = vtk.vtkDataSetMapper()
    gridMapper.SetInputData(reader.GetOutput())
    gridMapper.SetScalarRange(MIN_SCALAR, MAX_SCALAR)
    gridMapper.SetLookupTable(lut)

    # Actor
    print('Setting the Actor')
    gridActor = vtk.vtkActor()
    gridActor.SetMapper(gridMapper)

    # Render
    print('Setting the renderer')
    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)
    renderer.SetBackground(0.5, 0.5, 0.5)

    """
    We calculate the center of the map from
    the latitudes and longitudes given in the assignment
    """
    center_lat = (LAT_1 + LAT_2) / 2.0
    center_long = (LNG_1 + LNG_2) / 2.0
    altitude_focal = SEA_ALT
    altitude_pos = 505000

    renderer.ResetCameraClippingRange()
    renderer.GetActiveCamera().SetFocalPoint(coordinate_earth(center_lat, center_long, altitude_focal))
    renderer.GetActiveCamera().SetPosition(coordinate_earth(center_lat, center_long, altitude_pos))

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(600, 860)
    renWin.Render()

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    # Generates the .PNG file
    wif = vtk.vtkWindowToImageFilter()
    wif.SetInput(renWin)
    wif.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName("map_{}.png".format(SEA_ALT))
    writer.SetInputConnection(wif.GetOutputPort())
    writer.Write()

    print("Finish")

    # Interact with the data.
    iren.Initialize()
    iren.Start()


# Entry point of the application
main()

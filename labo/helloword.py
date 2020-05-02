import vtk as vtk


points = vtk.vtkPoints()
sgrid = vtk.vtkStructuredGrid()

def readInFile(filename):
    with open(filename, 'r', encoding="utf-8") as fd:
        dimensions = fd.readline().split(' ')
        lines = fd.readlines()

        data = []

        for line in lines:
            splits = line.split(' ')[:-1]
            for split in splits:
                data.append(float(split))

        return data, int(dimensions[0]), int(dimensions[1])


def initilizeData():
    data, Xs, Ys = readInFile('altitudes.txt')
    scalars = vtk.vtkFloatArray()


    # TODO comment detecter les lac ?

    for i in range(0, Xs):
        for j in range(0, Ys):
            index = j + (i * Xs)

            # TODO calcule courbre de la terre
            points.InsertNextPoint(i, j, data[index]*0.04)

            # TODO calcule du scalar
            scalars.InsertNextValue(data[index])

    sgrid.SetPoints(points)
    sgrid.SetDimensions([Xs, Ys, 1])
    sgrid.GetPointData().SetScalars(scalars)

    # TODO ecrire les donnée dans un ficher ? comme pour le cube
    

def main():

    initilizeData()


    # TODO modifier le lut pour afficher les bonnes couleurs : Ici c'est de la merde se que j'ai fait
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(10)
    lut.SetTableRange(0, 4783)
    lut.SetHueRange(0.6, 0.0)
    lut.SetSaturationRange(0.5, 0.0)
    lut.SetValueRange(0.6, 1.0)
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
    gridMapper.SetScalarRange(1, 2400) # TODO quel range mettre ?
    gridMapper.SetLookupTable(lut)

    # Actor
    gridActor = vtk.vtkActor()
    gridActor.SetMapper(gridMapper)

    # Render
    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)
    renderer.SetBackground(0, 0, 0)


    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(640, 640)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    renWin.Render()

    # Genere le fichier png
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName("map.png")
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()

    # Interact with the data.
    iren.Initialize()
    iren.Start()

main()
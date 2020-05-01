import vtk as vtk


def readFile(filename):
    with open(filename, 'r', encoding="utf-8") as fd:
        points = vtk.vtkPoints()
        fd.readline()

        x = 0
        y = 0

        lines = fd.readlines()

        print(len(lines))
        for line in lines:
            splits = line.split(' ')[:-1]

            for split in splits:
                points.InsertNextPoint([x, y, float(split)*0.04])
                x += 1
            y += 1
            x = 0

        return points


def main():
    print('Data acquisition...')
    points = readFile('altitudes.txt')

    print(points)

    dims = [3001, 3001, 1]

    grid = vtk.vtkStructuredGrid()
    grid.SetPoints(points)
    grid.SetDimensions(dims)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.0, 0.667)


    gridFilter = vtk.vtkStructuredGridGeometryFilter()
    gridFilter.SetInputData(grid)

    # Mapper
    gridMapper = vtk.vtkDataSetMapper()
    gridMapper.SetInputConnection(gridFilter.GetOutputPort())
    gridMapper.SetLookupTable(lut)
    # Actor
    gridActor = vtk.vtkActor()
    gridActor.SetMapper(gridMapper)
        # # Render
    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)
    renderer.SetBackground(0.3, 0.3, 0.4)


    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(640, 480)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Interact with the data.
    renWin.Render()
    iren.Start()

main()
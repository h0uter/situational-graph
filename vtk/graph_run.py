import vtkMod

def run(self):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0, 0, 0)

    camera = vtk.vtkCamera()
    camera.SetPosition((1, -1, -2))
    camera.SetViewUp((0, -1, 0))
    camera.SetFocalPoint((0, 0, 2))
    renderer.SetActiveCamera(camera)

    renwin = vtk.vtkRenderWindow()
    renwin.SetWindowName("Point Cloud Viewer")
    renwin.SetSize(800, 600)
    renwin.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interstyle = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(interstyle)
    interactor.SetRenderWindow(renwin)

    interactor.Initialize()

    cb = vtkTimerCallback(
        self.cinematic, self.render_path, self.clear_points)
    cb.queue = self.queue

    interactor.AddObserver('TimerEvent', cb.execute)
    timerId = interactor.CreateRepeatingTimer(100)

    #start the interaction and timer
    interactor.Start()


if __name__ == '__main__':
    run()

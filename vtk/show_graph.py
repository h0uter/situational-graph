import vtk
import time


def main():
  g = vtk.vtkMutableUndirectedGraph()


  # add your 15 vertices
  for i in range(15):
      g.AddVertex()

  t = [0, 2, 4, 5, 6, 8, 9, 11, 13, 1, 10, 1, 3, 7]
  h = [1, 3, 3, 1, 7, 7, 10, 12, 12, 14, 14, 12, 14, 10]

  # print(*zip(t,h))
  for start, end in zip(t, h):
    g.AddEdge(start, end)

  print('Number of vertices:', g.GetNumberOfVertices())
  print('Number of edges:', g.GetNumberOfEdges())
  graphLayoutView = vtk.vtkGraphLayoutView()
  graphLayoutView.AddRepresentationFromInput(g)
  graphLayoutView.ResetCamera()
  graphLayoutView.Render()
  graphLayoutView.GetInteractor().Start()

  time.sleep(2)
  # graphLayoutView.GetInteractor().End()


  for i in range(10):
      g.AddVertex()
  print('Number of vertices:', g.GetNumberOfVertices())

  t = [0, 2, 4, 5, 6, 8, 9, 11, 13]
  h = [1, 3, 3, 1, 7, 7, 10, 12, 12]

  # print(*zip(t,h))
  for start, end in zip(t, h):
    g.AddEdge(start, end)

  print('Number of edges:', g.GetNumberOfEdges())
  graphLayoutView = vtk.vtkGraphLayoutView()
  graphLayoutView.AddRepresentationFromInput(g)
  graphLayoutView.ResetCamera()
  graphLayoutView.Render()
  graphLayoutView.GetInteractor().Start()



if __name__ == '__main__':
    main()

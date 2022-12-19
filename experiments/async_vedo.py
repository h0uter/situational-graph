import asyncio

import vedo

class MySimulation:
    def __init__(self, name):
        self.name = name
        self.state = 0

    async def perform_calcs(self, viz):
        for i in range(100):
            self.state = i
            print(f"{self.name} {self.state}")
            await asyncio.sleep(0.1)

class MyVizualiser:
    def __init__(self):
        self.plt = vedo.Plotter()

    async def update(self, data):
        self.plt.clear()
        actor = vedo.Text3D(data, pos=(0, 0, 0), s=0.5)
        self.plt.show()


if __name__ == "__main__":
    simulation = MySimulation("Simulation")
    vizualiser = MyVizualiser()



    asyncio.run(asyncio.gather(simulation.perform_calcs(), vizualiser.update(simulation)))
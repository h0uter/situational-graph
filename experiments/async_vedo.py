import asyncio
import datetime
import time
import concurrent.futures

import numpy as np
import vedo

# vedo.settings.allow_interaction = True

'''I want to make my vizualisation async so it no longer blocks execution of the rest of my code'''

class MySimulation:
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.plt = vedo.Plotter()

    def update(self):
        while True:
            self.plt.clear()
            actor = vedo.Text2D(str(self.value))

            self.actual_blocking_viz_call(actor)
            
            # await asyncio.sleep(0)
            # self.plt.render()

            # if self.plt.escaped:
            #     quit()
    
    def actual_blocking_viz_call(self, actor):
        # self.plt.show(actor, interactive=True, resetcam=True)
        self.plt.show(actor, interactive=False, resetcam=True)


    async def perform_calcs(self):
        while True:

            self.value = np.random.random()

            await asyncio.sleep(self.value)

            print(f"{self.name} {self.value}")


    async def asynchronous(self):
        print("Create tasks", datetime.datetime.now().time())
        # task_1 = asyncio.create_task(self.perform_calcs())

        loop = asyncio.get_running_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        # task_2 = asyncio.create_task(self.update())
        task_2 = loop.run_in_executor(executor, self.update)

        # tasks = [task_1, task_2]
        tasks = [task_2]
        print("Tasks are created", datetime.datetime.now().time())
        
        await asyncio.wait(tasks)


async def main():
    sim = MySimulation("Simulation")
    # await sim.update(0)

    # await sim.loop()
    await sim.asynchronous()


# I want my counter to keep going as I block the vizualiser

if __name__ == "__main__":

    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


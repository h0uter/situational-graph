import asyncio
import time

def blocking():
    print("Started!")
    time.sleep(5)
    print("Finished!")

async def non_blocking():
    print("Started!")
    await asyncio.sleep(5)
    print("Finished!")

async def main():
    print("Blocking function:")
    start_time = time.time()
    await asyncio.gather(*(asyncio.to_thread(blocking) for i in range(5)))
    print("--- %s seconds ---" % (time.time() - start_time))

    print("Non-blocking function:")
    start_time = time.time()
    await asyncio.gather(*(non_blocking() for i in range(5)))
    print("--- %s seconds ---" % (time.time() - start_time))

asyncio.run(main())
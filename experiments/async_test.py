import asyncio

async def count_to_100():
    for i in range(100):
        print(i)
        await asyncio.sleep(0.2)


async def give_alphabet():
    for i in range(26):
        print(chr(ord("a") + i))
        await asyncio.sleep(1)


async def main():
    # await count_to_100()
    # await give_alphabet()

    # fut2 = await give_alphabet()
    # fut = await count_to_100()

    await asyncio.gather(give_alphabet(), count_to_100())


if __name__ == "__main__":
    asyncio.run(main())

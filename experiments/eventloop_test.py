import asyncio

async def say(what, when):
    print(f'{what} at {when}')
    await asyncio.sleep(1)
    print(f'{what} done')


loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(say('Hello', 'now'))
    loop.run_until_complete(say('World', 'later'))
finally:
    loop.close()
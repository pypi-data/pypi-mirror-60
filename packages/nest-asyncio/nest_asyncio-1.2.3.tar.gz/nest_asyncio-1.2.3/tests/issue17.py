import asyncio
import functools
import time

import nest_asyncio
nest_asyncio.apply()

def sync(corot):
    """
    Make a synchronous function from an asynchronous one.
    :param corot:
    :return:
    """
    result, = asyncio.get_event_loop().run_until_complete(asyncio.gather(corot))
    return result

async def sync_to_corountine(func, *args, **kw):
    """
    Make a coroutine from a synchronous function.
    """
    try:
        return func(*args, *kw)
    finally:
        # every async needs an await.
        await asyncio.sleep(0)

def main():
    async def background(timeout):
        await asyncio.sleep(timeout)
        print(f"Background: {timeout}")

    loop = asyncio.get_event_loop()
    # Run some bacground work to check we are never blocked
    bg_tasks = [
        loop.create_task(background(i))
        for i in range(10)
    ]

    async def long_running_async_task(result):
        # Simulate slow IO
        print(f"...START long_running_async_task [{result}]")
        await asyncio.sleep(4)
        print(f"...END   long_running_async_task [{result}]")
        return result

    def sync_function_with_async_dependency(result):
        print(f"...START sync_function_with_async_dependency [{result}]")
        result = sync(long_running_async_task(result))
        print(f"...END   sync_function_with_async_dependency [{result}]")
        return result

    # Call sync_function_with_async_dependency
    # One reentrant task is OK
    # Multiple reentrant tasks->fails to exit
    n = 2
    for i in range(n):
       bg_tasks.append(sync_to_corountine(sync_function_with_async_dependency, i))

    # OK
    # bg_tasks.append(long_running_async_task(123))
    # bg_tasks.append(long_running_async_task(456))

    task = asyncio.gather(*bg_tasks)  # , loop=loop)
    loop.run_until_complete(task)

if __name__ == '__main__':
    main()

import asyncio
import contextvars

import nest_asyncio
import pytest

# commenting out this line, the test suceeds
nest_asyncio.apply()

number_cv: contextvars.ContextVar[int] = contextvars.ContextVar('number_cv')


class TestContextVars:

    @pytest.mark.asyncio
    async def test_context_var(self):
        number_cv.set(1)

        await self.child_method()

        n = number_cv.get(-1)
        print(f'parent after child_method: number={n}')  # ok "parent after child_method: number=2"

        await asyncio.create_task(self.child_task())

        n = number_cv.get(-1)
        print(f'parent after child_task: number={n}')  # "parent after child_task: number=-1"
        assert n == 2

    async def child_method(self):
        n = number_cv.get(-1)
        print(f'in child_method: number={n}')  # ok "in child_method: number=1"
        number_cv.set(2)

    async def child_task(self):
        n = number_cv.get(-1)
        print(f'in child_task: number={n}')  # ok "in child_task: number=2"
        number_cv.set(3)
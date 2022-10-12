import asyncio
from datetime import datetime, timedelta
from typing import Generator

millisecond = milliseconds = 0.001
second = seconds = 1000 * milliseconds
minute = minutes = 60 * seconds
hour = hours = 60 * minutes
day = days = 24 * hours
week = weeks = 7 * days
other = 2


def schedule_repeating_action(loop, initial_delay, delay, action) -> None:
    def repeat():
        asyncio.ensure_future(action(), loop=loop)
        loop.call_later(delay, repeat)

    loop.call_later(initial_delay, repeat)


def schedule_at(times: Generator[datetime, None, None], action, loop) -> None:
    def call_action():
        asyncio.ensure_future(action(), loop=loop)

    def repeat():
        when = None
        done = False
        try:
            when = next(times)
        except StopIteration:
            done = True

        if not done:
            delay = (when - datetime.now()).total_seconds()
            loop.call_later(delay, call_action)
            loop.call_later(delay, repeat)

    loop.call_soon(repeat)


def timeiter(start: datetime, step: timedelta) -> Generator[datetime, None, None]:
    if step <= timedelta(0):
        raise ValueError('step must be positive')

    n = start
    while True:
        yield n
        n += step


class ScheduleWithStartOffset:
    def __init__(self, initial_delay: float, delay: float) -> None:
        self.initial_delay = initial_delay
        self.delay = delay

    def __call__(self, action, loop) -> None:
        schedule_repeating_action(loop, self.initial_delay, self.delay, action)


class ScheduleWithoutStartOffset:
    def __init__(self, delay: float) -> None:
        self.delay = delay

    def __call__(self, action, loop) -> ScheduleWithStartOffset:
        self.starting_in(0)(action, loop)

    def starting_in(self, initial_delay: float) -> ScheduleWithStartOffset:
        return ScheduleWithStartOffset(initial_delay, self.delay)

    def starting_at(self, hour: float, minute: float = 0) -> ScheduleWithStartOffset:
        now = datetime.now()
        start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if start < now:
            start += timedelta(days=1)
        initial_delay = (start - now).total_seconds()

        return ScheduleWithStartOffset(initial_delay, self.delay)


class EveryN:
    def __init__(self, n) -> None:
        self.milliseconds = ScheduleWithoutStartOffset(n * milliseconds)
        self.seconds = ScheduleWithoutStartOffset(n * seconds)
        self.minutes = ScheduleWithoutStartOffset(n * minutes)
        self.hours = ScheduleWithoutStartOffset(n * hours)
        self.days = ScheduleWithoutStartOffset(n * days)
        self.weeks = ScheduleWithoutStartOffset(n * weeks)


class EveryOther:
    def __init__(self) -> None:
        self.millisecond = ScheduleWithoutStartOffset(other * millisecond)
        self.second = ScheduleWithoutStartOffset(other * second)
        self.minute = ScheduleWithoutStartOffset(other * minute)
        self.hour = ScheduleWithoutStartOffset(other * hour)
        self.day = ScheduleWithoutStartOffset(other * day)
        self.week = ScheduleWithoutStartOffset(other * week)


class Every:
    def __init__(self) -> None:
        self.millisecond = ScheduleWithoutStartOffset(millisecond)
        self.second = ScheduleWithoutStartOffset(second)
        self.minute = ScheduleWithoutStartOffset(minute)
        self.hour = ScheduleWithoutStartOffset(hour)
        self.day = ScheduleWithoutStartOffset(day)
        self.week = ScheduleWithoutStartOffset(week)

        self.other = EveryOther()

    def __call__(self, n: float) -> EveryN:
        return EveryN(n)


every = Every()

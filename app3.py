#!/usr/bin/python3

import random
from bisect import insort
from datetime import datetime, timedelta
from enum import Enum, auto


class JobType(Enum):
    MINE_FOO = auto()
    MINE_BAR = auto()
    ASSEMBLE_FOOBAR = auto()
    SELL_FOOBAR = auto()
    BUY_ROBOT = auto()
    CHANGE = auto()

    def __str__(self):
        return f"{self.name}"


class Job:
    counter = 0

    def __init__(self, jtype, *, qty=None, destination=None):
        Job.counter += 1
        self._itemid = Job.counter
        self.jtype = jtype
        self.qty = qty
        self.destination = destination

    def __repr__(self):
        return f"<job #{self._itemid}: {self}>"

    def __str__(self):
        if self.qty:
            s = "s" if self.qty > 1 else ""
        if self.jtype == JobType.CHANGE:
            return f"‘moving to {self.destination}‘"
        if self.jtype == JobType.MINE_FOO:
            return f"‘mining {self.qty} foo{s}‘"
        if self.jtype == JobType.MINE_BAR:
            return f"‘mining {self.qty} bar{s}‘"
        if self.jtype == JobType.ASSEMBLE_FOOBAR:
            return f"‘assembling {self.qty} foobar{s}‘"
        if self.jtype == JobType.SELL_FOOBAR:
            return f"‘selling {self.qty} foobar{s}‘"
        if self.jtype == JobType.BUY_ROBOT:
            return f"‘buying {self.qty} robot{s}‘"


class Foo:
    counter = 0

    def __init__(self):
        Foo.counter += 1
        self._itemid = Foo.counter

    def __repr__(self):
        return f"<foo #{self._itemid}>"


class Bar:
    counter = 0

    def __init__(self):
        Bar.counter += 1
        self._itemid = Bar.counter

    def __repr__(self):
        return f"<bar #{self._itemid}>"


class Foobar:
    counter = 0

    def __init__(self, foo, bar):
        Foobar.counter += 1
        self.foo = foo
        self.bar = bar

    def __repr__(self):
        return f"<foobar #({self.foo!r}, {self.bar!r})>"


class Robot:
    counter = 0

    def __init__(self, job=None):
        Robot.counter += 1
        self._itemid = Robot.counter
        self.job = job
        self.rsrc = None
        self.endtime = None

    def __repr__(self):
        return f"<robot #{self._itemid}>"

    def __lt__(self, other):
        if self.endtime is None:
            return False
        if other.endtime is None:
            return True
        return self.endtime < other.endtime

    @staticmethod
    def _format_logsublist(msgs):
        return [f"├── {msg}" for msg in msgs[:-1]] + [f"└── {msgs[-1]}"]

    def report_load(self, duration):
        log = []
        log.append("")
        log.append((f"{self.job!r} assigned to {self}"))
        logitems = []
        logitems.append(f"duration: {duration} seconds")
        if self.rsrc.cash:
            logitems.append(f"{self.rsrc.cash}€ loaded")
        for rsrcitem in self.rsrc:
            logitems.append(f"{rsrcitem} loaded")
        log += self._format_logsublist(logitems)
        return log

    def report_unload(self, consumedrsrc, collectedrsrc):
        log = []
        log.append("")
        log.append(f"{self.job!r} done by {self}")
        logitems = []
        if self.job.jtype == JobType.CHANGE:
            logitems.append(f"moved to {self.job.destination!r}")
        elif self.job.jtype == JobType.MINE_FOO:
            for foo in collectedrsrc.foos:
                logitems.append(f"mined {foo}")
        elif self.job.jtype == JobType.MINE_BAR:
            for bar in collectedrsrc.bars:
                logitems.append(f"mined {bar}")
        elif self.job.jtype == JobType.ASSEMBLE_FOOBAR:
            for foobar in collectedrsrc.foobars:
                logitems.append(f"assembled {foobar}")
            for bar in collectedrsrc.bars:
                logitems.append(
                    f"failed to assemble a foobar; {bar} has been restored"
                )
            for foo in consumedrsrc.foos:
                logitems.append(f"consumed {foo}")
        elif self.job.jtype == JobType.SELL_FOOBAR:
            for foobar in consumedrsrc.foobars:
                logitems.append(f"sold {foobar}")
            if collectedrsrc.cash:
                logitems.append(f"collected {collectedrsrc.cash}€")
        elif self.job.jtype == JobType.BUY_ROBOT:
            for robot in collectedrsrc.robots:
                logitems.append(f"bought {robot}")
            if consumedrsrc.cash:
                logitems.append(f"spent {consumedrsrc.cash}€")
            for foo in consumedrsrc.foos:
                logitems.append(f"consumed {foo}")
        log += self._format_logsublist(logitems)
        return log

    def debug_unload(self):
        if not self.job:
            raise Exception(
                f"failed to unload {self}; has not been assigned"
            )
        if not self.rsrc:
            raise Exception(f"failed to unload {self}; has not been loaded")
        if not self.endtime:
            raise Exception(
                f"failed to unload {self}; has not been scheduled"
            )

    def debug_load(self):
        if self.job:
            raise Exception(
                f"failed to load {self}; has been assigned already"
            )
        if self.rsrc:
            raise Exception(
                f"failed to load {self}; has been loaded already"
            )
        if self.endtime:
            raise Exception(
                f"failed to load {self}; has been scheduled already"
            )


class Ressource:
    def __init__(
        self,
        rsrc=None,
        *,
        cash=0,
        foos=None,
        bars=None,
        foobars=None,
        robots=None,
    ):
        self.cash = cash
        self.foos = list(foos) if foos else []
        self.bars = list(bars) if bars else []
        self.foobars = list(foobars) if foobars else []
        self.robots = list(robots) if robots else []
        if rsrc:
            self += Ressource(
                cash=rsrc.cash,
                foos=rsrc.foos,
                bars=rsrc.foobars,
                robots=rsrc.robots,
            )

    def __str__(self):
        return (
            f"cash      {self.cash}\n"
            + f"foos      {len(self.foos)}\n"
            + f"bars      {len(self.bars)}\n"
            + f"foobars   {len(self.foobars)}\n"
            + f"robots    {len(self.robots)}"
        )

    def __add__(self, other):
        return Ressource(
            cash=self.cash + other.cash,
            foos=self.foos + other.foos,
            bars=self.bars + other.bars,
            foobars=self.foobars + other.foobars,
            robots=self.robots + other.robots,
        )

    def __iter__(self):
        return iter(self.foos + self.bars + self.foobars + self.robots)

    def extend(self, other):
        self += other

    def clear(self):
        self.cash = 0
        self.foos.clear()
        self.bars.clear()
        self.foobars.clear()
        self.robots.clear()


class Foobartory:
    def __init__(self, *, cash_start, nbrobots_start):
        self._log = []
        self.salesvolume = 0
        self.Job = Job
        self.Foo = Foo
        self.Bar = Bar
        self.Foobar = Foobar
        self.Robot = Robot
        self.schedule = []
        self.rsrc = Ressource(
            cash=cash_start,
            robots=[self.Robot() for _ in range(nbrobots_start)],
        )

    def start(self, nbrobots_max):
        self._realtime_start = datetime.now()
        self.virtualclock = 0
        self.print_elapsedtime()
        for robot in self.rsrc.robots:
            self.load(robot)
        self.print_inventory()
        self.print_report()
        while len(self.rsrc.robots) < nbrobots_max:
            robot = self.schedule.pop(0)
            waittime = robot.endtime - self.virtualclock
            if waittime > 0:
                self.virtualclock += waittime
            timer = datetime.now()
            self.print_elapsedtime()
            newrobots, previousjob = self.unload(robot)
            self.load(robot, previousjob)
            for newrobot in newrobots:
                self.load(newrobot)
            self.print_inventory()
            self.virtualclock += (datetime.now() - timer).total_seconds()
            self.print_report()
        self.print_finalreport()

    def load(self, robot, previousjob=None):
        robot.debug_load()
        self.assign_job(robot, previousjob)
        self.allocate_rsrc(robot)
        duration = random.uniform(*TIMING[robot.job.jtype])
        robot.endtime = self.virtualclock + duration
        insort(self.schedule, robot)
        self._log += robot.report_load(duration)

    def unload(self, robot):
        robot.debug_unload()
        consumedrsrc = Ressource()
        collectedrsrc = Ressource()
        if robot.job.jtype == JobType.MINE_FOO:
            collectedrsrc.foos += [self.Foo() for _ in range(robot.job.qty)]
        elif robot.job.jtype == JobType.MINE_BAR:
            collectedrsrc.bars += [self.Bar() for _ in range(robot.job.qty)]
        elif robot.job.jtype == JobType.ASSEMBLE_FOOBAR:
            for _ in range(robot.job.qty):
                foo = robot.rsrc.foos.pop(0)
                bar = robot.rsrc.bars.pop(0)
                if random.random() < 0.6:
                    consumedrsrc.foos += [foo]
                    consumedrsrc.bars += [bar]
                    collectedrsrc.foobars += [self.Foobar(foo, bar)]
                else:
                    consumedrsrc.foos += [foo]
                    collectedrsrc.bars += [bar]
        elif robot.job.jtype == JobType.SELL_FOOBAR:
            consumedrsrc.foobars += [
                robot.rsrc.foobars.pop(0) for _ in range(robot.job.qty)
            ]
            collectedrsrc.cash += robot.job.qty
            self.salesvolume += robot.job.qty
        elif robot.job.jtype == JobType.BUY_ROBOT:
            consumedrsrc.cash += robot.job.qty * 3
            robot.rsrc.cash -= robot.job.qty * 3
            consumedrsrc.foos += robot.rsrc.foos[: robot.job.qty * 6]
            del robot.rsrc.foos[: robot.job.qty * 6]
            collectedrsrc.robots += [
                self.Robot() for _ in range(robot.job.qty)
            ]
        self.rsrc += collectedrsrc + robot.rsrc
        self._log = robot.report_unload(consumedrsrc, collectedrsrc)
        previousjob = robot.job
        robot.job = robot.rsrc = robot.endtime = None
        return collectedrsrc.robots, previousjob

    def assign_job(self, robot, previousjob=None):
        if not previousjob:
            robot.job = Job(JobType.MINE_FOO, qty=1)
            return
        if self.rsrc.cash >= 3 and len(self.rsrc.foos) >= 6:
            jtype, qty = JobType.BUY_ROBOT, 1
        elif len(self.rsrc.foos) < 6:
            jtype, qty = JobType.MINE_FOO, 1
        elif len(self.rsrc.foobars) > 0:
            jtype, qty = JobType.SELL_FOOBAR, min(5, len(self.rsrc.foobars))
        elif len(self.rsrc.bars) > 0:
            jtype, qty = JobType.ASSEMBLE_FOOBAR, 1
        else:
            jtype, qty = JobType.MINE_BAR, 1
        if previousjob.jtype == jtype or (
            previousjob.jtype == JobType.CHANGE
            and previousjob.destination == jtype
        ):
            newjob = Job(jtype, qty=qty)
        else:
            newjob = Job(JobType.CHANGE, destination=jtype)
        robot.job = newjob

    def allocate_rsrc(self, robot):
        robot.rsrc = Ressource()
        if (
            robot.job.jtype == JobType.MINE_FOO
            or robot.job.jtype == JobType.MINE_BAR
            or robot.job.jtype == JobType.CHANGE
        ):
            pass
        elif robot.job.jtype == JobType.ASSEMBLE_FOOBAR:
            robot.rsrc.foos += self.rsrc.foos[: robot.job.qty]
            del self.rsrc.foos[: robot.job.qty]
            robot.rsrc.bars += self.rsrc.bars[: robot.job.qty]
            del self.rsrc.bars[: robot.job.qty]
        elif robot.job.jtype == JobType.SELL_FOOBAR:
            robot.rsrc.foobars += self.rsrc.foobars[: robot.job.qty]
            del self.rsrc.foobars[: robot.job.qty]
        elif robot.job.jtype == JobType.BUY_ROBOT:
            robot.rsrc.cash += robot.job.qty * 3
            self.rsrc.cash -= robot.job.qty * 3
            robot.rsrc.foos += self.rsrc.foos[: robot.job.qty * 6]
            del self.rsrc.foos[: robot.job.qty * 6]

    def print_elapsedtime(self):
        print("")
        print(
            f"***********************************************************"
        )
        print("")
        print(f"Elapsed time")
        print(f"------------")
        print(f"{datetime.now() - self._realtime_start} (real time)")
        print(f"{timedelta(seconds=self.virtualclock)} (simulated time)")

    def print_inventory(self):
        print("")
        print(f"Inventory")
        print(f"---------")
        print(str(self.rsrc))

    def print_report(self):
        for msg in self._log:
            print(msg)
        self._log.clear()

    def print_finalreport(self):
        print()
        print(f"Final stats")
        print(f"-----------")
        print(f"nb. of foos mined          {self.Foo.counter}")
        print(f"nb. of bars mined          {self.Bar.counter}")
        print(f"nb. of foobars assembled   {self.Foobar.counter}")
        print(f"nb. of scheduled jobs      {self.Job.counter}")
        print(f"volume of sales            {self.salesvolume}€")


TIMING = {
    JobType.MINE_FOO: (1, 1),
    JobType.MINE_BAR: (0.5, 2),
    JobType.ASSEMBLE_FOOBAR: (2, 2),
    JobType.CHANGE: (5, 5),
    JobType.SELL_FOOBAR: (10, 10),
    JobType.BUY_ROBOT: (0, 0),
}


if __name__ == "__main__":
    foobartory = Foobartory(cash_start=0, nbrobots_start=2)
    foobartory.start(nbrobots_max=30)
    print()

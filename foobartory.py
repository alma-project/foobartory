import random
from bisect import insort
from datetime import datetime, timedelta

from constants import TIMING
from items import Bar, Foo, Foobar, Robot
from job import Job, JobType
from ressource import Ressource


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
        self.print_report()
        while len(self.rsrc.robots) < nbrobots_max:
            robot = self.schedule.pop(0)
            waittime = robot.endtime - self.virtualclock
            if waittime > 0:
                self.virtualclock += waittime
            self.print_elapsedtime()
            timer = datetime.now()
            newrobots, previousjob = self.unload(robot)
            self.load(robot, previousjob=previousjob)
            for newrobot in newrobots:
                self.load(newrobot)
            self.virtualclock += (datetime.now() - timer).total_seconds()
            self.print_report()
        self.print_finalreport(nbrobots_max)

    def load(self, robot, *, previousjob=None):
        robot.debug_load()
        self.assign_job(robot, previousjob=previousjob)
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

    def assign_job(self, robot, *, previousjob=None):
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
        print()
        print(
            f"***********************************************************"
        )
        print("")
        print(f"Elapsed time")
        print(f"------------")
        print(f"simulated   {timedelta(seconds=self.virtualclock)}")
        print(f"real        {datetime.now() - self._realtime_start}")

    def print_inventory(self):
        print()
        print(f"Inventory")
        print(f"---------")
        print(self.rsrc)

    def print_report(self):
        self.print_inventory()
        for msg in self._log:
            print(msg)
        self._log.clear()

    def print_finalreport(self, nbrobots_max):
        print()
        print(
            f"***********************************************************"
        )
        print()
        print(f" Objective reached: {nbrobots_max} robots")
        self.print_elapsedtime()
        self.print_inventory()
        print()
        print(f"Final stats")
        print(f"-----------")
        print(f"nb. of foos mined          {self.Foo.counter}")
        print(f"nb. of bars mined          {self.Bar.counter}")
        print(f"nb. of foobars assembled   {self.Foobar.counter}")
        print(f"nb. of scheduled jobs      {self.Job.counter}")
        print(f"volume of sales            {self.salesvolume}€")

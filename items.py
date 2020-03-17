from job import JobType


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
        logitems.extend([f"{rsrcitem} loaded" for rsrcitem in self.rsrc])
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
            logitems.extend([f"mined {foo}" for foo in collectedrsrc.foos])
        elif self.job.jtype == JobType.MINE_BAR:
            logitems.extend([f"mined {bar}" for bar in collectedrsrc.bars])
        elif self.job.jtype == JobType.ASSEMBLE_FOOBAR:
            logitems.extend(
                [f"assembled {foobar}" for foobar in collectedrsrc.foobars]
            )
            logitems.extend(
                [
                    f"failed to assemble a foobar; {bar} has been restored"
                    for bar in collectedrsrc.bars
                ]
            )
            logitems.extend(
                [f"consumed {foo}" for foo in consumedrsrc.foos]
            )
        elif self.job.jtype == JobType.SELL_FOOBAR:
            logitems.extend(
                [f"sold {foobar}" for foobar in consumedrsrc.foobars]
            )
            if collectedrsrc.cash:
                logitems.append(f"collected {collectedrsrc.cash}€")
        elif self.job.jtype == JobType.BUY_ROBOT:
            logitems.extend(
                [f"bought {robot}" for robot in collectedrsrc.robots]
            )
            if consumedrsrc.cash:
                logitems.append(f"spent {consumedrsrc.cash}€")
            logitems.extend(
                [f"consumed {foo}" for foo in consumedrsrc.foos]
            )
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

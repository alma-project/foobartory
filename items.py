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
        return f"<foobar ({self.foo!r}, {self.bar!r})>"


class Robot:
    counter = 0

    def __init__(self, *, job=None, rsrc=None, endtime=None):
        Robot.counter += 1
        self._itemid = Robot.counter
        self.job = job
        self.rsrc = rsrc
        self.endtime = endtime

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
        if not msgs:
            return []
        return [f"├── {msg}" for msg in msgs[:-1]] + [f"└── {msgs[-1]}"]

    def report_load(self, duration):
        log = [""]
        log += [f"{self.job!r} assigned to {self}"]
        logitems = []
        logitems += [f"duration {duration} seconds"]
        if self.rsrc.cash:
            logitems += [f"{self.rsrc.cash}€ allocated"]
        logitems += [f"{rsrcitem} allocated" for rsrcitem in self.rsrc]
        log += self._format_logsublist(logitems)
        return log

    def report_unload(self, consumedrsrc, collectedrsrc):
        log = [""]
        log += [f"{self.job!r} done by {self}"]
        logitems = []
        if collectedrsrc.cash:
            logitems += [f"{collectedrsrc.cash}€ collected"]
        logitems += [f"{foo} mined" for foo in collectedrsrc.foos]
        logitems += [
            f"{bar} mined"
            for bar in collectedrsrc.bars
            if self.job.jtype == JobType.MINE_BAR
        ]
        logitems += [
            f"failed to assemble a foobar; {bar} restored"
            for bar in collectedrsrc.bars
            if self.job.jtype == JobType.SELL_FOOBAR
        ]
        logitems += [
            f"{foobar} assembled" for foobar in collectedrsrc.foobars
        ]
        logitems += [f"{robot} acquired" for robot in collectedrsrc.robots]
        if consumedrsrc.cash:
            logitems += [f"{consumedrsrc.cash}€ spent"]
        logitems += [f"{foo} consumed" for foo in consumedrsrc.foos]
        logitems += [f"{bar} consumed" for bar in consumedrsrc.bars]
        logitems += [f"{foobar} sold" for foobar in consumedrsrc.foobars]
        log += self._format_logsublist(logitems)
        return log

    def debug_unload(self):
        if not self.job:
            raise Exception(f"failed to unload {self}; no job assigned")
        if not self.rsrc:
            raise Exception(
                f"failed to unload {self}; no ressource allocated"
            )
        if not self.endtime:
            raise Exception(
                f"failed to unload {self}; has not been scheduled"
            )

    def debug_load(self):
        if self.job:
            raise Exception(f"failed to load {self}; job already assigned")
        if self.rsrc:
            raise Exception(
                f"failed to load {self}; ressource already allocated"
            )
        if self.endtime:
            raise Exception(
                f"failed to load {self}; has been scheduled already"
            )

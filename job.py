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

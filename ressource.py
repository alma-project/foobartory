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

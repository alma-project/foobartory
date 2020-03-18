from job import JobType

TIMING = {
    JobType.MINE_FOO: (1, 1),
    JobType.MINE_BAR: (0.5, 2),
    JobType.ASSEMBLE_FOOBAR: (2, 2),
    JobType.CHANGE: (5, 5),
    JobType.SELL_FOOBAR: (10, 10),
    JobType.BUY_ROBOT: (0, 0),
}

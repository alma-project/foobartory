#!/usr/bin/python3

import random
from functools import partial
from datetime import datetime, timedelta
from abc import ABC, abstractmethod, abstractproperty

    
class Item():
    compound = []
        
    def __init__(self, item_id, **kwargs):
        keys1 = [ cls._item_type for cls in self.compound ]
        keys2 = [ key for key in kwargs.keys() ]
        assert keys1 == keys2
        self.id = tuple(kwargs.values()) if self.compound else item_id

    def __repr__(self):
        if self.compound:
            return '{} {}'.format(self._item_type, self.id)
        else:
            return '{} #{}'.format(self._item_type, self.id)

    def __str__(self):
        return '<{!r}>'.format(self)


class Robot(Item):    
    pass


class Process(Item):
    def __init__(self, item_id, *, task, robot, endtime, trigger):
        self.id = item_id
        self.task = task
        self.robot = robot
        self.endtime = endtime
        self._trigger = trigger

    def complete(self):
        print(self, 'has been completed by', self.robot) 
        self._trigger(self.robot)


class Factory(ABC):     
    def __init__(self, *, stock_classes, cash, nb_robots):
        self._counter = {}
        self._item_classes = {}
        
        for cls in stock_classes + [Robot, Process]:
            item_type = cls.__name__.lower()
            cls._item_type = item_type
            self._counter[item_type] = 0
            self._item_classes[item_type] = cls
            setattr(self, item_type + 's', [])            

        self.cash = cash

        for _ in range(nb_robots):
            new_robot = self.new('robot')
            self.robots.append(new_robot)

        self._counter['process'] = 0
        self.schedule = []
            
    def new(self, item_type, **kwargs):
        self._counter[item_type] += 1
        return self._item_classes[item_type](
            item_id = self._counter[item_type],
            **kwargs )

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def order(self, robot, *, prev_task):
        pass
    
    @abstractmethod
    def report(self):
        pass
    

class Foo(Item):
    pass


class Bar(Item):
    pass


class Foobar(Item):
    compound = [Foo, Bar]


class Foobartory(Factory):
    def __init__(self, *, stock_classes, cash, nb_robots, timings):
        self._timings = timings
        super().__init__(
            stock_classes=stock_classes,
            nb_robots=nb_robots,
            cash=cash )

    def leadtime(self, task):
        duration = self._timings[task]
        if len(duration) == 1:
            duration = duration[0]
        elif len(duration) == 2:
            duration = random.uniform(duration[0], duration[1])
        return datetime.now() + timedelta(
            seconds=duration * self._timings['_coeff'])
        
    def store_foo(self, robot):
        new_foo = self.new('foo')
        self.foos.append(new_foo)
        print(new_foo, 'has been mined by', robot)

    def store_bar(self, robot):
        new_bar = self.new('bar')
        self.bars.append(new_bar)
        print(new_bar, 'has been mined by', robot)


    def store_foobar(self, robot, *, foo, bar):
        if random.random() < 0.6:
            new_foobar = self.new('foobar', foo=foo, bar=bar)
            self.foobars.append(new_foobar)
            print(new_foobar, 'has been mined by', robot)

        else:
            self.bars.append(bar)
            print(robot, 'has failed to assemble a foobar')
            print(foo, 'has been lost')
            print(bar, 'has been restored')
    
    def sell_foobar(self, robot, *, foobars):
        self.cash += len(foobars)
        for fb in foobars:
            print(fb, 'has been sold by', robot)

    def buy_robot(self, robot, *, nb_orders):
        for _ in range(nb_orders):
            new_robot = self.new('robot')
            self.robots.append(new_robot)
            print(new_robot, 'has been bought by', robot)
            self.order(new_robot)      

    def start(self):
        start_time = datetime.now()
        current_time = start_time

        self.report()
        
        for robot in self.robots:
            self.order(robot)

        while len(self.robots) < 30:
            if current_time >= self.schedule[0].endtime:
                process = self.schedule.pop(0)
                process.complete()
                self.order(process.robot, prev_task=process.task)
                self.report()
            current_time = datetime.now()

        print()
        print('Completed in {} (simulated time)'.format(
            (current_time - start_time) / self._timings['_coeff']))
        print()

    def order(self, robot, prev_task=None):
        nb_foos = len(self.foos)
        nb_bars = len(self.bars)
        nb_foobars = len(self.foobars)
        cash = self.cash

        if cash >= 3 and nb_foos >= 6:
            new_task='buy_robot'
            nb_orders = min(cash // 3, nb_foos // 6)
                    
        elif nb_foos < 6:
            new_task='mine_foo'

        elif nb_foobars > 0:
            new_task='sell_foobar'
            nb_orders = min(5, nb_foobars)

        elif nb_bars > 0:
            new_task='assemble_foobar'

        else:
            new_task='mine_bar'
    
        move_task = "move_to_{}".format(new_task)
        if prev_task != new_task and prev_task != move_task:
            new_task = move_task

        if 'move_to' in new_task:
            trigger = lambda rb : None

        elif 'mine_foo' == new_task:
            trigger = self.store_foo

        elif 'mine_bar' == new_task:
            trigger = self.store_bar

        elif 'assemble_foobar' == new_task:
            foo = self.foos.pop()
            bar = self.bars.pop()
            trigger = partial(self.store_foobar, foo=foo, bar=bar)

        elif 'sell_foobar' == new_task:
            foobars = []
            for _ in range(nb_orders):
                foobars.append(self.foobars.pop())
            trigger = partial(self.sell_foobar, foobars=foobars)

        elif 'buy_robot' == new_task:
            self.cash -= 3 * nb_orders
            for _ in range(6 * nb_orders):
                self.foos.pop()
            trigger = partial(self.buy_robot, nb_orders=nb_orders)

        new_process = self.new('process',
            task = new_task,
            robot = robot,
            endtime = self.leadtime(new_task),
            trigger = trigger )
        self.schedule.append(new_process)
        self.schedule.sort(key=lambda proc: proc.endtime)

        print("{} has a new task: '{}'".format(robot, new_task))

    def report(self):
        fstr = '{:19}{}'
        print()
        print(fstr.format('foos in stock', len(self.foos)))
        print(fstr.format('bars in stock', len(self.bars)))
        print(fstr.format('foobars in stock', len(self.foobars)))
        print(fstr.format('cash available', self.cash))
        print(fstr.format('number of robots', len(self.robots)))
        print(fstr.format('current time', datetime.now()))
        print()
        print()
        print()

        
foobartory = Foobartory(
    stock_classes = [Foo, Bar, Foobar],
    cash = 0,
    nb_robots = 2,
    timings = {
        '_coeff': 0.001,
        'mine_foo': [1],
        'mine_bar': [0.5, 2],
        'assemble_foobar': [2],
        'sell_foobar': [10],
        'buy_robot': [0],
        'move_to_mine_foo': [5],
        'move_to_mine_bar': [5],
        'move_to_assemble_foobar': [5],
        'move_to_sell_foobar': [5],
        'move_to_buy_robot': [5] } )

foobartory.start()

#!/usr/bin/python3

import random
from functools import partial
from bisect import insort
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

    
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

    def enter(self, list):
        list.append(self)


class Robot(Item):    
    pass


class Process(Item):
    def __init__(self, item_id, *, endtime, job, robot, ressources):
        super().__init__(item_id)
        self.endtime = endtime
        self.job = job
        self.robot = robot
        self.ressources = ressources

    def __lt__(self, other):
        return self.endtime < other.endtime

    def enter(self, list):
        insort(list, self)
        

class Factory(ABC):     
    def __init__(self, *, stock_classes, cash_start,
                 nb_robots_start, nb_robots_max):
        self._counter = {}
        self._item_classes = {}
        self._ressources = {}
        
        for cls in stock_classes + [Robot, Process]:
            item_type = cls.__name__.lower()
            cls._item_type = item_type
            self._counter[item_type] = 0
            self._item_classes[item_type] = cls
            self._ressources[item_type] = []            

        for _ in range(nb_robots_start):
            new_robot = self.new('robot')

        self.cash = cash_start
        self._nb_robots_max = nb_robots_max
        self._timestart = datetime.now()

    def list(self, item_type):
        return self._ressources[item_type]
        
    def count(self, item_type):
        return len(self.list(item_type))
            
    def new(self, item_type, **kwargs):
        self._counter[item_type] += 1
        if item_type == 'process':
            new_item = self._item_classes[item_type](
                item_id = self._counter[item_type],
                endtime = self.compute_endtime(kwargs['job']),
                **kwargs)
        else:
            new_item = self._item_classes[item_type](
                item_id = self._counter[item_type],
                **kwargs )
        new_item.enter(self.list(item_type))
        return new_item

    def add(self, item_type, new_item):
        self.list(item_type).append(new_item)

    def remove(self, item_type):
        return self._ressources[item_type].pop(0)

    @property
    def elapsed_time(self):
        elapsed_time = datetime.now() - self._timestart
        return elapsed_time / self._timings['_coeff']

    @property
    def is_waiting(self):
        leading_process = self.list('process')[0]
        job = leading_process.job
        endtime = leading_process.endtime
        return datetime.now() < endtime

    @abstractmethod
    def compute_endtime(self, job):
        pass
    
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def allocate(self, *args):
        pass

    @abstractmethod
    def allocate(self, *args):
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
    def __init__(self, timings, **kargs):
        self._timings = timings
        super().__init__(**kargs)

    def compute_endtime(self, job):
        duration = self._timings[job]
        if len(duration) == 1:
            duration = duration[0]
        elif len(duration) == 2:
            duration = random.uniform(duration[0], duration[1])
        return datetime.now() + timedelta(
                seconds=duration * self._timings['_coeff'])
    
    def start(self):
        print('Foobartory started...')
        print()
        
        for robot in self.list('robot'):
            self.new('process',
                     job = 'mine_foo',
                     robot = robot,
                     ressources = {} )
        
        while self.count('robot') < self._nb_robots_max:
            
            if not self.is_waiting:
                process = self.remove('process')
                self.complete(process)
                self.allocate(process.robot, prev_job=process.job)
                self.report()
        
        fstr = '{:19}{}'    
        print(fstr.format(
            'processes created', self._counter['process']))
        print(fstr.format(
            'foos mined', self._counter['foo']))
        print(fstr.format(
            'bars mined', self._counter['bar']))
        print(fstr.format(
            'foobars assembled', self._counter['foobar']))
        
        print()

    def allocate(self, robot, prev_job=None):
        nb_foos = self.count('foo')
        nb_bars = self.count('bar')
        nb_foobars = self.count('foobar')
        cash = self.cash

        if cash >= 3 and nb_foos >= 6:
            new_job='buy_robot'
            nb_orders = min(cash // 3, nb_foos // 6)
                    
        elif nb_foos < 6:
            new_job='mine_foo'

        elif nb_foobars > 0:
            new_job='sell_foobar'
            nb_orders = min(5, nb_foobars)

        elif nb_bars > 0:
            new_job='assemble_foobar'

        else:
            new_job='mine_bar'
    
        move_job = "move_to_{}".format(new_job)
        if prev_job != new_job and prev_job != move_job:
            new_job = move_job

        if ( 'move_to' in new_job or
             'mine_foo' == new_job or
             'mine_bar' == new_job ):
            ressources = {}

        elif 'assemble_foobar' == new_job:
            foo = self.remove('foo')
            bar = self.remove('bar')
            ressources = { 'foo': [foo], 'bar': [bar] }

        elif 'sell_foobar' == new_job:
            foobars = []
            for _ in range(nb_orders):
                foobars.append(self.remove('foobar'))
            ressources = { 'foobar': foobars }

        elif 'buy_robot' == new_job:
            self.cash -= 3 * nb_orders
            for _ in range(6 * nb_orders):
                self.remove('foo')
            ressources = { 'cash': 3 * nb_orders }

        new_process = self.new('process',
            job = new_job,
            robot = robot,
            ressources = ressources)

        print()
        print(new_process, 'has begun')
        print("└── {} has a new job: '{}'".format(robot, new_job))

    def complete(self, process):
        print()
        print(process, 'has been completed')

        job = process.job
        robot = process.robot
        ressources = process.ressources

        def print_sublist(fstr, arg, list):
            for x in list[:-1]:
                print('├──', fstr.format(arg, x))
            print('└──', fstr.format(arg, list[-1]))
 
        if 'move_to_' in job:
            dest_job = job.split('move_to_')[1]
            print("└── {} has moved to the job '{}'".format(robot, dest_job))

        elif 'mine_foo' == job:
            new_foo = self.new('foo')
            print('└──', new_foo, 'has been mined by', robot)

        elif 'mine_bar' == job:
            new_bar = self.new('bar')
            print('└──', new_bar, 'has been mined by', robot)

        elif 'assemble_foobar' == job:
            foo = ressources['foo'][0]
            bar = ressources['bar'][0]
            if random.random() < 0.6:
                new_foobar = self.new('foobar', foo=foo, bar=bar)
                print('└──', new_foobar, 'has been mined by', robot)
            else:
                self.add('bar', bar)
                print('└──', robot, 'has failed to assemble a foobar')
                print(foo, 'has been lost')
                print(bar, 'has been restored')

        elif 'sell_foobar' == job:
            foobars = ressources['foobar']
            self.cash += len(foobars)
            print_sublist('{} has sold {}', robot, foobars)
        
        elif 'buy_robot' == job:
            nb_orders = ressources['cash'] // 3
            new_robots = []
            for _ in range(nb_orders):
                new_robots.append(self.new('robot'))
            print_sublist('{} has bought {}', robot, new_robots) 
            for rb in new_robots: self.allocate(rb)

    def report(self):
        fstr = '{:19}{}'
        print()
        print(fstr.format('foos in stock', self.count('foo')))
        print(fstr.format('bars in stock', self.count('bar')))
        print(fstr.format('foobars in stock', self.count('foobar')))
        print(fstr.format('cash available', self.cash))
        print(fstr.format('number of robots', self.count('robot')))
        print((fstr + ' {}').format(
            'elapsed time', self.elapsed_time, '(simulated)'))
        print('...')
        print()

        
foobartory = Foobartory(
    stock_classes = [Foo, Bar, Foobar],
    cash_start = 0,
    nb_robots_start = 2,
    nb_robots_max = 30,
    timings = {
        '_coeff': 1,
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

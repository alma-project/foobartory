#!/usr/bin/python3

import random
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
        return '<{}>'.format(self.__repr__())

class Robot(Item):    
    def __init__(self, item_id):
        super().__init__(item_id)
        self.task = None


class Process():
    def __init__(self, *, robot, endtime, trigger):
        self.robot = robot
        self.endtime = endtime
        self._trigger = trigger

    def complete(self):
        print('task',  "'{}'".format(self.robot.task),
            'completed by robot', self.robot)
        self._trigger()


class Factory(ABC):     
    def __init__(self, *, stock_classes, cash, nb_robots):
        self._counter = {}
        self._item_classes = {}
        
        for cls in stock_classes + [Robot]:
            item_type = cls.__name__.lower()
            cls._item_type = item_type
            self._counter[item_type] = 0
            self._item_classes[item_type] = cls
            setattr(self, item_type + 's', [])            

        self.cash = cash
        self.schedule = []
        self.enroll(nb_robots)

    def new(self, item_type, **kwargs):
        self._counter[item_type] += 1
        return self._item_classes[item_type](
            item_id = self._counter[item_type],
            **kwargs )

    def enroll(self, nb_robots):
        for _ in range(nb_robots):
            new_robot = self.new('robot')
            self.robots.append(new_robot)
            self.order(new_robot)

    @abstractmethod
    def order(self, robot):
        pass

    @abstractmethod
    def start(self):
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
        return datetime.now() + timedelta(seconds=duration/100)
        
    def store_foo(self):
        new_foo = self.new('foo')
        self.foos.append(new_foo)
        print('\n', new_foo, 'has been successfully mined') 

    def store_bar(self):
        new_bar = self.new('bar')
        self.bars.append(new_bar)
        print('\n', new_bar, 'has been successfully mined') 

    def store_foobar(self, *, foo, bar):
        if random.random() < 0.6:
            new_foobar = self.new('foobar', foo=foo, bar=bar)
            self.foobars.append(new_foobar)
            print('\n', new_foobar, 'has been successfully assembled')
        else:
            self.bars.append(bar)
            print(
                '\nfoobar assembly has failed',
                '\n', foo, 'has been lost,', bar, 'has been restored' )
    
    def sell_foobar(self, foobars):
        self.cash += len(foobars)
        for fb in foobars:
            print('\n', fb, 'has been solded')

    def buy_robot(self, nb_orders):
        self.enroll(nb_orders)      
            
    def order(self, robot):
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
        if (
                robot.task == new_task or
                robot.task == move_task
        ):
            robot.task = new_task
            
        else:
            robot.task = move_task

        if 'move_to' in robot.task:
            trigger = lambda : None

        elif 'mine_foo' == robot.task:
            trigger = lambda : self.store_foo()

        elif 'mine_bar' == robot.task:
            trigger = lambda : self.store_bar()

        elif 'assemble_foobar' == robot.task:
            foo = self.foos.pop()
            bar = self.bars.pop()
            trigger = lambda : self.store_foobar(foo=foo, bar=bar)

        elif 'sell_foobar' == robot.task:
            foobars = []
            for _ in range(nb_orders):
                foobars.append(self.foobars.pop())
            trigger = lambda : self.sell_foobar(foobars)

        elif 'buy_robot' == robot.task:
            self.cash -= 3 * nb_orders
            for _ in range(6 * nb_orders):
                self.foos.pop()
            trigger = lambda : self.buy_robot(nb_orders)
            
        self.schedule.append(Process(
            robot = robot,
            endtime = self.leadtime(robot.task),
            trigger = trigger ))
            
    def start(self):
        start_time = datetime.now()
        current_time = start_time
        
        while len(self.robots) < 30:
            if current_time >= self.schedule[0].endtime:
                print('\nCurrent time:', current_time)
                process = self.schedule.pop(0)
                process.complete()
                self.order(process.robot)   

                print(
                    '\nnumber of foos in stock: ', len(self.foos),
                    '\nnumber of bars in stock: ', len(self.bars),
                    '\nnumber of foobars in stock: ', len(self.foobars),
                    '\ncash available: ', '{}€'.format(self.cash),
                    '\nnumber of robots: ', len(self.robots),
                    '\n' )
            current_time = datetime.now()

        print(
            '\nCompleted in', current_time - start_time,
            '\n\n' )

foobartory = Foobartory(
    stock_classes = [Foo, Bar, Foobar],
    cash = 0,
    nb_robots = 2,
    timings = {
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

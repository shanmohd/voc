from unittest import expectedFailure

from ..utils import TranspileTestCase


class GeneratorTests(TranspileTestCase):
    def test_simple_generator(self):
        self.assertCodeExecution("""
            def multiplier(first, second):
                y = first * second
                yield y
                y *= second
                yield y
                y *= second
                yield y
                y *= second
                yield y

            print(list(multiplier(1, 20)))
            """)

    def test_loop_generator(self):
        self.assertCodeExecution("""
            def fizz_buzz(start, stop):
                for i in range(start, stop):
                    found = False
                    if i % 2 == 0:
                        yield 'fizz'
                        found = True
                    if i % 3 == 0:
                        yield 'buzz'
                        found = True
                    if not found:
                        yield i

            print(list(fizz_buzz(1, 20)))
            """)

    def test_simplest_generator(self):
        self.assertCodeExecution("""
            def somegen():
                yield 1
                yield 2
                yield 3

            for i in somegen():
                print(i)
            """)

    def test_generator_method(self):
        self.assertCodeExecution("""
            class Interview:
                def __init__(self, start, stop):
                    self.start = start
                    self.stop = stop

                def fizz_buzz(self):
                    for i in range(self.start, self.stop):
                        found = False
                        if i % 2 == 0:
                            yield 'fizz'
                            found = True
                        if i % 3 == 0:
                            yield 'buzz'
                            found = True
                        if not found:
                            yield i

            myinterview = Interview(1, 20)

            for i in myinterview.fizz_buzz():
                print(i)
            """)

    def test_yield_from_not_used(self):
        """Yield from is currently not implemented.
        Unused yield from statements must not break
        the program compilation, but only ensue a warning."""
        self.assertCodeExecution("""
            def unused():
                yield from range(5)

                print('Hello, world!')
            """)

    @expectedFailure
    def test_yield_from_used(self):
        """Yield from is currently not implemented.
        Yield from statements become NotImplementedErrors at runtime."""
        self.assertCodeExecution("""
            def using_yieldfrom():
                yield from range(5)

            for i in using_yieldfrom():
                print(i)
            """)

    def test_generator_send(self):
        self.assertCodeExecution("""
            def gen():
                a = yield
                print(a)

            g = gen()
            next(g)
            try:
                g.send("Hello World")
            except StopIteration:
                pass
            """)

    def test_generator_multi_send(self):
        self.assertCodeExecution("""
            def gen():
                a = yield 1
                print(a)
                b = yield 2
                print(b)

            g = gen()
            next(g)
            try:
                print(g.send("a"))
                print(g.send("b"))
            except StopIteration:
                pass
            """)

    def test_generator_send_loop(self):
        self.assertCodeExecution("""
            def gen():
                for i in range(1, 5):
                    a = yield i
                    print("printing from generator " + str(a))

            g = gen()
            g.send(None)
            try:
                while True:
                    b = g.send(1)
                    print("printing from user " + str(b))
            except StopIteration:
                pass
            """)

    def test_generator_yield_expr_call(self):
        self.assertCodeExecution("""
            def gen():
                while True:
                    x = print((yield))

            g = gen()
            g.send(None)
            g.send("Hello World")
            """)

    def test_generator_yield_expr_unary_op(self):
        self.assertCodeExecution("""
            def gen():
                while True:
                    x = -(yield)
                    yield x

            g = gen()
            g.send(None)
            g.send(2)
            g.send(-1)
            """)

    def test_generator_yield_expr_bool_op(self):
        self.assertCodeExecution("""
            def gen():
                while True:
                    x = not (yield)
                    yield x

            g = gen()
            g.send(None)
            g.send(True)
            g.send(False)
            """)

    def test_generator_yield_expr_binary_op(self):
        self.assertCodeExecution("""
            def gen():
                while True:
                    x = 2 + (yield)
                    yield x

            def gen2():
                while True:
                    x = (yield) * 2
                    yield x

            def gen3():
                while True:
                    x = (yield) ** 2
                    yield x

            g = gen()
            g.send(None)
            g.send(2)
            g.send(-1)

            g = gen2()
            g.send(None)
            g.send(100)
            g.send(20)

            g = gen3()
            next(g)
            g.send(2)
            g.send(0)
            """)

    def test_generator_yield_expr_aug_assign(self):
        self.assertCodeExecution("""
            def gen():
                while True:
                    x = 2
                    x += (yield)
                    yield x

            g = gen()
            g.send(None)
            g.send(1)
            g.send(2)
            """)

    def test_generator_yield_expr_compare(self):
        self.assertCodeExecution("""
            def gen():
                while True:
                    x = 1 <= (yield) < 5
                    yield x

            g = gen()
            g.send(None)
            g.send(1)
            g.send(100)
            """)

    def test_generator_yield_expr_if(self):
        self.assertCodeExecution("""
            def gen():
                if (yield):
                    print("Hello world")

            g = gen()
            g.send(None)
            try:
                g.send(1)
            except StopIteration:
                pass
            """)

    @expectedFailure
    def test_generator_yield_expr_return(self):
        self.assertCodeExecution("""
            def gen():
                return (yield)

            g = gen()
            g.send(None)
            g.send(1)  # for some reason the generator keeps returning value
            g.send(100) # without raising StopIteration error
            """)

    def test_generator_throw_on_starting(self):
        self.assertCodeExecution("""
            def gen():
                yield "Hello World"

            g = gen()
            try:
                g.throw(ZeroDivisionError)
            except ZeroDivisionError:
                pass
            """)

    def test_generator_throw_other_exception(self):
        self.assertCodeExecution("""
            def gen():
                try:
                    yield
                    print("Hello World")
                except ZeroDivisionError:
                    raise TypeError
                    
                print("") # temporary fix for no 'next_op'

            g = gen()
            next(g)
            try:
                g.throw(ZeroDivisionError)
            except TypeError:
                pass
            """)

    def test_generator_throw_complex(self):
        self.assertCodeExecution("""
            def gen():
                try:
                    yield "from try block"
                except TypeError:
                    yield "from catch block"

                yield "from outside try-except"
                a = yield
                print(a)

            g = gen()
            print(next(g))
            print(g.throw(TypeError))
            print(next(g))
            print(g.send("message"))
            """)

    def test_generator_close(self):
        self.assertCodeExecution("""
            def gen():
                print("Hello world")
                try:
                    yield
                except TypeError:
                    pass
                except ZeroDivisionError:
                    pass

            g = gen()
            print(g.close())
            try:
                print(next(g))
            except StopIteration:
                pass
            """)

    def test_generator_close_ignore_exit(self):
        self.assertCodeExecution("""
            def gen():
                try:
                    yield
                except TypeError:
                    pass
                except GeneratorExit:
                    yield "exit ignored"

            g = gen()
            next(g)
            try:
                g.close()
            except RuntimeError:
                pass
            """)

    def test_generator_close_exception_propagation(self):
        self.assertCodeExecution("""
            def gen():
                try:
                    yield
                except GeneratorExit:
                    raise OSError

                print("") # temporary fix for no 'next_op'

            g = gen()
            next(g)
            try:
                g.close()
            except OSError:
                pass
            """)

    def test_generator_close_twice(self):
        self.assertCodeExecution("""
            def gen():
                yield 1
                yield 2

            g = gen()
            print(g.close())
            print(g.close())
            """)

    @expectedFailure
    def test_generator_yield_no_next_op(self):
        self.assertCodeExecution("""
            def gen():
                try:
                    yield
                except:
                    raise StopIteration
            """)

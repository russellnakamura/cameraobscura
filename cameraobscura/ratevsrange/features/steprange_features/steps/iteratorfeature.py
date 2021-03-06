
# python standard library
from random import randrange

# third party
from behave import then, when, given
from hamcrest import assert_that, contains

# this package
from cameraobscura.ratevsrange.stepiterator import StepRange

@given("StepRange start less than stop and no step thresholds")
def start_lt_stop(context):
    stop = randrange(-100, 100)
    start = stop - randrange(abs(stop))
    context.iterator = StepRange(start=start,
                                 stop=stop)
    return

@when("the StepRange is traversed")
def step_traversal(context):
    context.traversal = [step for step in context.iterator]
    return

@then("the StepRange output is a range from start to stop")
def assert_range(context):
    # the 'range' includes the last value
    assert_that(context.traversal,
                contains(*range(context.iterator.start,
                                context.iterator.stop + 1,
                                context.iterator.step_size)))
    return

@given("StepRange start less than stop and one step thresholds")
def start_lt_stop(context):
    start = 0
    stop = 10
    step_sizes = (1, 2)
    step_thresholds = [6]
    context.iterator = StepRange(stop=stop,
                                 start=start,
                                 step_sizes=step_sizes,
                                 step_change_thresholds=step_thresholds)
    return

@then("the StepRange output is a stepped range from start to stop")
def assert_range(context):
    # the 'range' includes the last value
    expected = range(7) + [8, 10]
    assert_that(context.traversal,
                contains(*expected))
    return

@given("StepRange start greater than stop and no step thresholds")
def start_gt_stop(context):
    start = randrange(1, 100)
    stop = 0

    context.iterator = StepRange(stop=stop,
                                 start=start)
    return

@then("the StepRange output is a descending range from start to stop")
def assert_range(context):
    # the 'range' includes the last value
    expected = range(context.iterator.start,
                     context.iterator.stop-1,
                     -context.iterator.step_sizes[0])
    assert_that(context.traversal,
                contains(*expected))
    return
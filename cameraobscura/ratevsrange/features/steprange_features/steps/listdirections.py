
# python standard library
from random import randrange

# third-party
from behave import then, when, given
from hamcrest import assert_that, contains

# this package
from cameraobscura.ratevsrange.stepiterator import StepRange

@given("a StepRange that is reversed multiple times")
def multiple_reversals(context):
    start = 0
    stop = 9
    context.iterator = StepRange(start=start, stop=stop)
    return

@when("the StepRange list_directions are checked")
def check_list_directions(context):
    directions = []
    for reversal in xrange(randrange(100)):
        context.iterator.reversals = reversal
        directions.append(context.iterator.list_direction)
    context.list_directions = directions
    return

@then("the StepRange list_directions alternate")
def assert_list_directions(context):
    direction = -1
    expected = []
    for reversal in xrange(context.iterator.reversals + 1):
        direction *= -1
        expected.append(direction)

    print context.list_directions
    assert_that(context.list_directions,
                contains(*expected))
    return
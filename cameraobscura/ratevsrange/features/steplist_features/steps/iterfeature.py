
# third-party
from behave import given, when, then
from hamcrest import assert_that, is_, equal_to, contains

# this package
from cameraobscura.ratevsrange.stepiterator import StepList

@given("a StepList that moves in the upward direction")
def upward_steplist(context):
    context.expected = range(10)
    context.iterator = StepList(step_list=context.expected)
    return

@when("the iteration is checked")
def check_iteration(context):
    context.steps = [step for step in context.iterator]
    return

@then("the values are the expected for the upward")
def assert_values(context):
    assert_that(context.steps,
                is_(equal_to(context.expected)))
    return

@given("a StepList that moves in the downward direction")
def upward_steplist(context):
    context.expected = range(10, 0, -1)
    context.iterator = StepList(step_list=context.expected)
    return

@then("the values are the expected for the downward")
def assert_values(context):
    assert_that(context.steps,
                contains(*context.expected))
    return

@given("a StepList that moves in the up and down direction")
def up_and_down_steplist(context):
    context.range = range(10)
    context.iterator = StepList(step_list=context.range)
    return

@then("the values are the expected for the up and down")
def assert_values(context):
    context.iterator.reset()
    context.iterator.reversal_limit = 1
    expected = range(6) + range(4, -1, -1)
    actual = []

    for step in context.iterator:
        actual.append(step)
        if step == 5:
            print "reverse"
            context.iterator.reverse()
    print actual
    assert_that(actual,
                contains(*expected))
    return
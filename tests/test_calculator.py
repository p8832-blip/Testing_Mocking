import pytest
from ..task_calculator import Calculator

def test_add_two_numbers_correctly():
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5


"""
Contains a few simple math functions.
"""
import operator
from typing import Tuple
from math import floor, log10


INFINITE = float( 'Inf' )


def increment_mean( mean: float, count: int, new_value: float ) -> Tuple[float, int]:
    new_count = count + 1
    new_mean = mean + ((new_value - mean) / new_count)
    return new_mean, new_count


def safe_div( a, b ):
    if b == 0:
        return INFINITE
    
    return a / b


def percent( a, b ):
    return a, safe_div( a, b )


operators = { "==": operator.eq,
              "!=": operator.ne,
              ">" : operator.gt,
              "<" : operator.lt,
              ">=": operator.ge,
              "<=": operator.le }


def round_significant( x, s = 2 ):
    if x==0:
        return x
    
    return round( x, s - int( floor( log10( abs( x ) ) ) ) - 1 )

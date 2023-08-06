from enum import auto, Enum
from typing import List, Sequence

from mhelper import arg_parser
from mhelper._unittests._test_base import test, testing

class ETestEnum(Enum):
    ALPHA=auto()
    BETA=auto()
    GAMMA=auto()
    DELTA=auto()

def test_function( alpha: int, beta: str = "default", *, gamma: Sequence[int], delta: Sequence[str] = ("DEFAULT",), epsilon: bool = False, zeta: bool = True, eta: bool,
                   theta: ETestEnum):
    """
    Help for test_function goes here.
    
    :param alpha:      Help for parameter alpha goes here.  
    :param beta:       Help for parameter beta goes here.  
    :param gamma:      Help for parameter gamma goes here.  
    :param delta:      Help for parameter delta goes here.  
    :param epsilon:    Help for parameter epsilon goes here.  
    :param zeta:       Help for parameter zeta goes here.  
    :param eta:        Help for parameter eta goes here.
    :return: 
    """
    print( "TEST FUNCTION" )
    print( f"    alpha  = {alpha!r}" )
    print( f"    beta   = {beta!r}" )
    print( f"    gamma  = {gamma!r}" )
    print( f"    delta  = {delta!r}" )
    print( f"    epsilon= {epsilon!r}" )
    print( f"    zeta   = {zeta!r}" )
    print( f"    eta    = {eta!r}" )
    print( f"    theta  = {theta!r}" )


@test
def test_from_function():
    arg_parser.args_to_function( test_function, "--alpha 1 --beta A --gamma 1 2 3 --delta A B C --no_epsilon --zeta --eta --theta GAMMA".split( " " ) )
    arg_parser.args_to_function( test_function, [])


if __name__ == "__main__":
    test.execute()

from enum import Enum

from mhelper.documentation_helper import get_enum_documentation, get_basic_documentation, Documentation

from mhelper._unittests._test_base import test, testing


class MyEnum( Enum ):
    """
    My enum.
    
    :cvar ALPHA: Hello once
    :cvar BETA: Hello twice
    """
    ALPHA = 1
    BETA = 2


@test
def test_documentation():
    """
    This is the documentation string.
    
    .. note::
    
        This is the notes string
    
    :param one:     One text line one
                    One text line two
                    One text line three
    :param two:     Two text line one
                        Two text line two indented.
                        Two text line three indented.
    :return:        Return text.
    :exception three: Value
                      Value
    """
    
    doc = Documentation( test_documentation.__doc__ )
    
    print( "********** - - **********\n{}\n**********".format( doc[""][""] ) )
    print( "********** param one **********\n{}\n**********".format( doc["param"]["one"] ) )
    print( "********** param two **********\n{}\n**********".format( doc["param"]["two"] ) )
    print( "********** return - **********\n{}\n**********".format( doc["return"][""] ) )
    print( "********** MyEnum **********\n{}\n**********".format( get_basic_documentation( MyEnum ) ) )
    print( "********** MyEnum.ALPHA **********\n{}\n**********".format( get_enum_documentation( MyEnum.ALPHA ) ) )


if __name__ == "__main__":
    test.execute()

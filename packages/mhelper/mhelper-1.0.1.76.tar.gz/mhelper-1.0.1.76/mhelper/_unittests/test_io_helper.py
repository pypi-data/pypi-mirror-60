import json
from enum import Enum

from mhelper import io_helper
from ._test_base import test, testing


class ETest( Enum ):
    ALPHA = 1
    BETA = 2
    GAMMA = 3


@test
def open_write_doc():
    testing( io_helper.open_write_doc() ).IS_READABLE( "Open write documentation generator" )


@test
def json_enum():
    obj = dict( alpha = ETest.ALPHA,
                beta = ETest.BETA,
                another = dict( gamma = ETest.GAMMA ),
                string = "Nothing::Nothing"
                )
    txt = io_helper.EnumJsonEncoder( supported_enums = [ETest] ).encode( obj )
    obj2 = io_helper.EnumJsonDecoder( supported_enums = [ETest] ).decode( txt )
    
    testing( obj2 ).EQUALS( obj )


if __name__ == "__main__":
    test.execute()

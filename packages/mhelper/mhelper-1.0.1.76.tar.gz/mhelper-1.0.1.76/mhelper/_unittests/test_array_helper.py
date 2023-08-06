from mhelper import array_helper
from mhelper._unittests._test_base import test, testing


@test
def test_remover():
    my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    with array_helper.Remover( my_list ) as my_list_:
        for item in my_list_:
            if item % 2 == 0:
                my_list_.drop()
    
    testing( my_list ).EQUALS( [1, 3, 5, 7, 9] )


if __name__ == "__main__":
    test.execute()

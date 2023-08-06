from mhelper import utf_table
from ._test_base import test, testing


@test
def test_table():
    expected = (
        #I xxxxx I xxxxxxxxxx I 
        "| One   | Two three  |\n"
        "|       | four five  |\n"
        "|       | six        |\n"
        "| ONE   | TWO THREE  |\n"
        "|       | FOUR FIVE  |\n"
        "|       | SIX        |\n"
    ).replace( "|", "│" )
    t = utf_table.TextTable( (5, 10) )
    t.add_wrapped( ("One", "Two three four five six") )
    t.add_wrapped( ("ONE", "TWO THREE FOUR FIVE SIX") )
    testing( t.to_string() ).EQUALS( expected )


if __name__ == "__main__":
    test.execute()

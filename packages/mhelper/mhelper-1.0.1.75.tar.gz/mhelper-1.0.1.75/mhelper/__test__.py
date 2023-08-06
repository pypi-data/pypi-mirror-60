import unittest
from typing import Optional, Union

import jsonpickle

from mhelper import array_helper, batch_lists, string_helper, ansi_helper, ansi
from mhelper.batch_lists import BatchList
from mhelper.mannotation import AnnotationInspector
from mhelper.property_helper import itemproperty
from mhelper.serialisable import Serialisable


class MyClassSerialisable( Serialisable ):
    __slots__ = "a", "b", "c", "__d", "__e", "__f"
    
    
    def __init__( self ):
        super().__init__()
        self.a = 1
        self.b = 2
        self.c = 3
        self.__d = 4
        self.__e = 5
        self.__f = 6
    
    
    def _SERIALISABLE_state( self ):
        yield MyClassSerialisable, "c", 3.1
        yield MyClassSerialisable, "__f", 6.1
    
    
    def set_values( self ):
        self.a = -1
        self.b = -2
        self.c = -3
        self.__d = -4
        self.__e = -5
        self.__f = -6
    
    
    def __str__( self ):
        return "{} {} {} {} {} {}".format( self.a, self.b, self.c, self.__d, self.__e, self.__f )


class serialisable_helper_tests( unittest.TestCase ):
    __slots__ = ()
    
    
    def test_functionality( self ):
        original = MyClassSerialisable()
        original.set_values()
        
        encoded = jsonpickle.encode( original )
        decoded = jsonpickle.decode( encoded )
        
        self.assertEqual( str( original ), "-1 -2 -3 -4 -5 -6" )
        self.assertEqual( str( decoded ), "-1 -2 3.1 -4 -5 6.1" )


class property_helper_tests( unittest.TestCase ):
    __slots = ()
    
    
    def test_decorator( self ):
        class temporary:
            __slots__ = ("items",)
            
            
            def __init__( self ):
                self.items = { }
            
            
            @itemproperty
            def blah( self, key ):
                return self.items[key]
            
            
            @blah.itemsetter
            def blah( self, key, value ):
                self.items[key] = value
        
        
        a = temporary()
        
        a.blah[5] = "555"
        a.blah[8] = "888"
        self.assertEqual( a.blah[5], "555" )
        self.assertEqual( a.blah[8], "888" )


class ansi_helper_tests( unittest.TestCase ):
    __slots__ = ()
    
    
    def test_functions( self ):
        # TODO: These tests should check the output automatically
        
        my_text = ansi.FORE_RED + "RED" + ansi.FORE_GREEN + "GREEN" + ansi.FORE_BLUE + "BLUE" + ansi.RESET
        my_text_2 = (my_text + " ") * 20
        
        for width in (5, 10, 15):
            print( "            [" + "." * width + "]" )
            print( "fix_width = [{}]".format( ansi_helper.fix_width( my_text, width ) ) + ansi.RESET )
            print( "fix_width = [{}]".format( ansi_helper.fix_width( my_text, width, "~", -1 ) ) + ansi.RESET )
            print( "fix_width = [{}]".format( ansi_helper.fix_width( my_text, width, "~", 0 ) ) + ansi.RESET )
            print( "fix_width = [{}]".format( ansi_helper.fix_width( my_text, width, "~", 1 ) ) + ansi.RESET )
            print( "ljust     = [{}]".format( ansi_helper.ljust( my_text, width, "~" ) ) + ansi.RESET )
            print( "cjust     = [{}]".format( ansi_helper.cjust( my_text, width, "~" ) ) + ansi.RESET )
            print( "rjust     = [{}]".format( ansi_helper.rjust( my_text, width, "~" ) ) + ansi.RESET )
        
        print( "length    = [{}]".format( ansi_helper.length( my_text ) ) + ansi.RESET )
        print( "without   = [{}]".format( ansi_helper.without_ansi( my_text ) ) + ansi.RESET )
        print( "wrap20,80 = [{}]".format( "\n".join( ansi_helper.wrap( my_text_2, 80 ) ) ) + ansi.RESET )
        print( "add2      = [{}]".format( my_text + my_text ) + ansi.RESET )
        print( "multiply3 = [{}]".format( my_text * 3 ) + ansi.RESET )


class string_helper_tests( unittest.TestCase ):
    __slots__ = ()
    
    
    def test_percent( self ):
        self.assertEqual( string_helper.percent( 0.5 ), "50.0%" )
        self.assertEqual( string_helper.percent( q = 0.5 ), "50.0%" )
        self.assertEqual( string_helper.percent( 5, 10, t = 1 ), "50.0%" )
        self.assertEqual( string_helper.percent( 5, 10 ), "5 (50.0%)" )
        self.assertEqual( string_helper.percent( 5, 10, t = 3 ), "5/10 (50.0%)" )
        self.assertEqual( string_helper.percent( 5, 0 ), "5 (inf%)" )
        self.assertEqual( string_helper.percent( 0, 0 ), "0 (0%)" )
        self.assertEqual( string_helper.percent( q = 0.5, d = 10 ), "5 (50.0%)" )
        self.assertEqual( string_helper.percent( q = 0.5, d = 10, t = 3 ), "5/10 (50.0%)" )
    
    
    def test_format_array( self ):
        a = ["hello1", "hello2", "hello3", "lemon5", "lemon6", "lemon9", "apple"]
        s = string_helper.format_array( a, sort = True, autorange = True, join = "," )
        self.assertEqual( s, "apple,hello1-3,lemon5-6,lemon9" )
    
    
    def test_highlight_quotes( self ):
        self.assertEqual( string_helper.highlight_quotes( "hello 'world' hello's", "'", "'", "<", ">" ), "hello <world> hello's" )
        self.assertEqual( string_helper.highlight_quotes( "alpha 'beta' gamma 'delta'", "'", "'", "<", ">" ), "alpha <beta> gamma <delta>" )
    
    
    def test_fix_indents( self ):
        text_a = """alpha\n\n        beta\n            gamma\n                delta\n        epsilon\n    """
        text_b = """alpha\n\nbeta\n    gamma\n        delta\nepsilon\n"""
        self.assertEqual( string_helper.fix_indents( text_a ), text_b )


class array_helper_tests( unittest.TestCase ):
    __slots__ = ()
    
    
    def test_ranges( self ):
        r = array_helper.list_ranges( (1, 2, 3, 4, 10, 11, 12, 13, 100, 101, 102, 103) )
        self.assertEqual( r, [(1, 4), (10, 13), (100, 103)] )
    
    
    def test__create_index_lookup( self ):
        """
        TEST: create_index_lookup
        """
        
        my_list = "a", "b", "c", "d", "e"
        
        lookup = array_helper.create_index_lookup( my_list )
        
        # Sanity check
        for i, v in enumerate( my_list ):
            self.assertEqual( i, lookup[v] )


class batch_lists_test( unittest.TestCase ):
    __slots__ = ()
    
    
    def test__BatchList__take( self ):
        b = BatchList( (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 3 )
        
        self.assertEqual( b.take(), [1, 2, 3] )
        self.assertEqual( b.take(), [4, 5, 6] )
        self.assertEqual( b.take(), [7, 8, 9] )
        self.assertEqual( b.take(), [10, ] )
    
    
    def test__divide_workload( self ):
        self.assertEqual( batch_lists.divide_workload( 0, 5, 51 ), (0, 10) )
        self.assertEqual( batch_lists.divide_workload( 1, 5, 51 ), (10, 20) )
        self.assertEqual( batch_lists.divide_workload( 2, 5, 51 ), (20, 30) )
        self.assertEqual( batch_lists.divide_workload( 3, 5, 51 ), (30, 40) )
        self.assertEqual( batch_lists.divide_workload( 4, 5, 51 ), (40, 51) )
    
    
    def test__divide_workload_2( self ):
        last_b = None
        for i in range( 1000 ):
            a, b = batch_lists.divide_workload( i, 1000, 1600 )
            
            self.assertGreater( b, a )
            
            if last_b is not None:
                self.assertEqual( a, last_b )
            
            last_b = b


class reflection_helper_tests( unittest.TestCase ):
    __slots__ = ()
    
    
    def test__annotations( self ):
        # noinspection PyClassHasNoInit
        class UPPER:
            __slots__ = ()
        
        
        # noinspection PyClassHasNoInit
        class MIDDLE( UPPER ):
            __slots__ = ()
        
        
        # noinspection PyClassHasNoInit
        class LOWER( MIDDLE ):
            __slots__ = ()
        
        
        # noinspection PyClassHasNoInit
        class DIFFERENT:
            __slots__ = ()
        
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_indirect_subclass_of( UPPER ) )
        self.assertTrue( AnnotationInspector( Optional[MIDDLE] ).is_indirect_subclass_of( UPPER ) )
        self.assertTrue( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirect_subclass_of( UPPER ) )
        self.assertFalse( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirect_subclass_of( LOWER ) )
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_direct_subclass_of( UPPER ) )
        self.assertFalse( AnnotationInspector( Optional[MIDDLE] ).is_direct_subclass_of( UPPER ) )
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_indirectly_superclass_of( LOWER ) )
        self.assertTrue( AnnotationInspector( Optional[MIDDLE] ).is_indirectly_superclass_of( LOWER ) )
        self.assertTrue( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirectly_superclass_of( LOWER ) )
        self.assertFalse( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirectly_superclass_of( UPPER ) )
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_direct_superclass_of( LOWER ) )
        self.assertFalse( AnnotationInspector( Optional[MIDDLE] ).is_direct_superclass_of( LOWER ) )
        
        middle = MIDDLE()
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_viable_instance( middle ) )
        self.assertTrue( AnnotationInspector( Optional[UPPER] ).is_viable_instance( middle ) )
        self.assertTrue( AnnotationInspector( Union[LOWER, UPPER] ).is_viable_instance( middle ) )
        self.assertFalse( AnnotationInspector( Union[LOWER] ).is_viable_instance( middle ) )


class MathsHelper_test( unittest.TestCase ):
    __slots__ = ()
    
    
    def test_increment_mean( self ):
        from mhelper import maths_helper
        
        my_values = [1, 7, 23, 2, 6, 2, 6, 8, 42, 9, 3, 1, 0.2, 0.3]
        
        incremental_average = 0
        incremental_count = 0
        
        for index, new_value in enumerate( my_values ):
            incremental_average, incremental_count = maths_helper.increment_mean( incremental_average, incremental_count, new_value )
            true_average = sum( my_values[:index + 1] ) / (index + 1)
            self.assertAlmostEqual( incremental_average, true_average )
            self.assertEqual( incremental_count, index + 1 )


if __name__ == '__main__':
    unittest.main()

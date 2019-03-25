import unittest
from mrtd import MRTD
from pypassport.reader import TimeOutException
from pypassport.doc9303.mrz import MRZException

class TestPassportClass(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestPassportClass, self).__init__(*args, **kwargs)

        self.valid_mrz = "ABCD01A236???9001011?2001012<<<<<<<<<<<<<<06"

    def test_mrz_string(self):
        mrz = ['ABCD01A23', '900101', '200101']
        mrtd = MRTD(mrz)

        self.assertEqual(mrtd.mrz_string, "ABCD01A236???9001011?2001012<<<<<<<<<<<<<<06")

    def test_valid_mrz_1(self):
        """
        Valid MRZ
        """
        input = ['ABCD01A23', '900101', '200101']
        mrtd = MRTD(input)

        valid = mrtd.check_mrz()

        self.assertTrue(valid)
    
    def test_valid_mrz_2(self):
        """
        Invalid MRZ, document number too long
        """
        input = ['ABCD01A23<', '900101', '200101']
        mrtd = MRTD(input)

        with self.assertRaises(MRZException) as context:
            mrtd.check_mrz()
        
        self.assertTrue("The mrz length is invalid" in context.exception)
    
    def test_valid_mrz_3(self):
        """
        Invalid MRZ, date of birth too long
        """
        input = ['ABCD01A23', '900101<', '200101']
        mrtd = MRTD(input)

        with self.assertRaises(MRZException) as context:
            mrtd.check_mrz()
        
        self.assertTrue("The mrz length is invalid" in context.exception)
    
    def test_valid_mrz_4(self):
        """
        Invalid MRZ, experation date too long
        """
        input = ['ABCD01A23', '900101', '200101<']
        mrtd = MRTD(input)

        with self.assertRaises(MRZException) as context:
            mrtd.check_mrz()
        
        self.assertTrue("The mrz length is invalid" in context.exception)

    def test_valid_mrz_5(self):
        """
        Invalid MRZ, every element too short
        """        
        input = ['ABCD01A2', '90010', '20010']
        mrtd = MRTD(input)

        with self.assertRaises(MRZException) as context:
            mrtd.check_mrz()
        
        self.assertTrue("The mrz length is invalid" in context.exception)


if __name__ == '__main__':
    unittest.main()

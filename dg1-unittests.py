import unittest
from mrtd import MRTD

class TestPassportClass(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestPassportClass, self).__init__(*args, **kwargs)
        self.valid_mrz = "ABCD01A236???9001011?2001012<<<<<<<<<<<<<<06"
    
    def test_name_format_1(self):
        input = "JANSEN<<JAN<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        expected_output = ["Jansen", "Jan"]

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_name(input)

        self.assertEqual(output, expected_output)

    def test_name_format_2(self):
        input = "JANSEN<<JAN<FRANK<JOS<<<<<<<<<<<<<<<<<<"
        expected_output = ["Jansen", "Jan Frank Jos"]

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_name(input)

        self.assertEqual(output, expected_output)

    def test_name_format_3(self):
        input = "VAN<DER<MEULEN<<MARTIN<<<<<<<<<<<<<<<<<"
        expected_output = ["Van Der Meulen", "Martin"]

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_name(input)

        self.assertEqual(output, expected_output)

    def test_name_format_4(self):
        input = "SMITH<JONES<<SUSIE<MARGARET<<<<<<<<<<<<"
        expected_output = ["Smith Jones", "Susie Margaret"]

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_name(input)

        self.assertEqual(output, expected_output)

    def test_date_format_1(self):
        input = "900201"
        expected_output = "1990-02-01"

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_date(input)

        self.assertEqual(output, expected_output)

    def test_date_format_2(self):
        input = "021228"
        expected_output = "2002-12-28"

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_date(input)

        self.assertEqual(output, expected_output)

    def test_date_format_3(self):
        input = "080101"
        """
        Testing edge case
        """
        expected_output = "2008-01-01"

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_date(input)

        self.assertEqual(output, expected_output)

    def test_date_format_4(self):
        """
        Testing edge case
        """
        input = "090101"
        expected_output = "1909-01-01"

        mrtd = MRTD(self.valid_mrz)
        output = mrtd.format_date(input)

        self.assertEqual(output, expected_output)

    def test_date_format_5(self):
        """
        Testing edge cases
        """
        input_a = "060101"
        expected_output_a = "2006-01-01"

        input_b = "070101"
        expected_output_b = "1907-01-01"

        adjustment_years = 12

        mrtd = MRTD(self.valid_mrz)
        output_a = mrtd.format_date(input_a, adjustment_years)
        output_b = mrtd.format_date(input_b, adjustment_years)

        self.assertEqual(output_a, expected_output_a)
        self.assertEqual(output_b, expected_output_b)

if __name__ == '__main__':
    unittest.main()

from pypassport.reader import ReaderManager, TimeOutException
from pypassport.epassport import EPassport, mrz
from pypassport.doc9303 import tagconverter
from pypassport.doc9303.bac import BACException
from pypassport.iso7816 import Iso7816Exception

from image_handler import convert_jp2

import json, logging
from datetime import datetime

class MRTD:
    """
    Machine Readable Travel Document

    TODO:
    - add doc
    """
    def __init__(self, mrz=None, output=False):
        if(type(mrz) is list):
            #                    doc_nr, dob,    exp_nr
            mrz = self._buildMRZ(mrz[0], mrz[1], mrz[2])

        self.mrz_string = mrz
        self.output = output
        self.epassport = None
        self.reader_obj = None
        self.dg1_retries = 0
        self.dg2_retries = 0
        self.max_retries = 3
    
    def do_bac(self):
        self.epassport.doBasicAccessControl()

    def _set_reader_obj(self):
        if self.reader_obj != None:
            return
        
        rm = ReaderManager()
        logging.info("Waiting for card...")
        try:
            self.reader_obj = rm.waitForCard()
        except TimeOutException as e:
            logging.warn("Retrying after '{}'".format(e.message))
            return self._set_reader_obj()

        logging.info("Card detected!")
    
    def check_mrz(self, mrz_string):
        mrz_obj = mrz.MRZ(mrz_string)
        return mrz_obj.checkMRZ()
    
    def _set_epassport(self):
        if self.check_mrz(self.mrz_string) == False:
            logging.warn("MRZ is not valid")
            return False
        
        self._set_reader_obj()

        self.epassport = EPassport(self.reader_obj, self.mrz_string)
        return True

    def personal_data(self):
        self._set_epassport()

        try:
            if self.dg1_retries == self.max_retries:
                logging.info("Reposition ID-card and try again")
                return

            if self.dg1_retries > 0:
                logging.info("Retry count: {}".format(self.dg1_retries))

            dg1_data = self.epassport['DG1']
        except Iso7816Exception as e:
            logging.exception(e.message)
            logging.info("Retrying...")
            self.dg1_retries += 1
            return self.personal_data()
        except BACException as e:
            logging.exception(e.message)
            logging.info("Possible mismatch MRZ and document")
            return None


        clean_info = {}
        for attribute, value in dg1_data.iteritems():
            tag_name = tagconverter.tagToName[attribute]
            clean_info.update({tag_name: value})
        
        if self.output:
            doc_number_tag = '5A'
            doc_number = dg1_data[doc_number_tag]

            with open('output/' + doc_number + '.json', 'w') as outfile:
                json.dump(clean_info, outfile)

        return clean_info

    def photo_data(self, output_format='jpeg'):
        if self._set_epassport() == False:
            logging.error("EPassport not set")
            return

        logging.info("Getting image from NFC, this might take a while...")

        try:
            if self.dg2_retries == self.max_retries:
                logging.info("Reposition ID-card and try again")
                return

            if self.dg2_retries > 0:
                logging.info("Retry count: {}".format(self.dg2_retries))

            dg2_data = self.epassport['DG2']
        except Iso7816Exception as e:
            logging.exception(e.message)
            logging.info("Retrying...")
            self.dg2_retries += 1
            return self.photo_data()
        except BACException as e:
            logging.exception(e.message)
            logging.info("Possible mismatch MRZ and document")
            return None


        # check from ePassportviewer
        if dg2_data['A1'].has_key('5F2E'): tag = '5F2E' # 5F2E: Biometric data block 
        elif dg2_data['A1'].has_key('7F2E'): tag = '7F2E' # 7F2E: Biometric data block (enciphered) 

        img_data = dg2_data['A1'][tag]

        if self.output:
            dg1_data = self.epassport['DG1']
            doc_number_tag = '5A'
            output_name = dg1_data[doc_number_tag]
        else:
            output_name = 'tmp'

        return convert_jp2(img_data, output_name, output_format, self.output)

    def format_name(self, input):
        """
        Formats a name as taken from DG1 to a readable format
        Returns a list with the surname as first element and first name as second element,
        e.g. ["Van Der Meulen", "Martin"]

        :param input: e.g. "VAN<DER<MEULEN<<MARTIN<<<<<<<<<<<<<<<<<"
        """
        index_end_surname = input.index("<<")
        surname = input[:index_end_surname]
    
        if surname.find("<") == -1:
            surname = surname.lower().capitalize()
        else:
            surname_list = surname.split("<")

            surname = ""
            i = 0
            for name in surname_list:
                surname += name.lower().capitalize()
                if i != len(surname_list)-1:
                    surname += " "
                i += 1

        first_name = input[index_end_surname:]
        first_name = first_name[2:]

        index_end = first_name.index("<<")
        first_name = first_name[:index_end]

        if first_name.find("<") == -1:
            first_name = first_name.lower().capitalize()
        else:
            first_name_list = first_name.split("<")

            first_name = ""
            i = 0
            for name in first_name_list:
                first_name += name.lower().capitalize()                
                if i != len(first_name_list)-1:
                    first_name += " "
                i += 1

        full_name = []
        full_name.append(surname)
        full_name.append(first_name)
        return full_name

    def format_date(self, input, adjustment_years=10):
        """
        Formats a date as taken from DG1 (yymmdd) to a standard format (yyyy-mm-dd).

        In this function the standard date formatting of Python is adjusted to fit the use case.
        With Pythons default datetime will format '69' to '1969' and '68' to '2068'.
        So all the years after '69 will be concidered 20th century and before '69 as 21st century.

        This is changed to where the switch in century interpretation is x years before the current year.
        This means as for today, 4th December 2018, i.e. '08' is '2008' and '09' is '1909'

        :param input: year in format 'yymmdd'
        :param adjustment_years: amount of years before current year what will be the new turn of century

        """
        date_obj = datetime.strptime(input, '%y%m%d')

        current_year = datetime.now().year

        if date_obj.year > current_year - adjustment_years:
            date_obj = date_obj.replace(year=date_obj.year-100)

        date = date_obj.strftime("%Y-%m-%d")

        return date

    # From pypassport > attacks > bruteForce
    def _buildMRZ(self, id_pass, dob, exp, pers_num="<<<<<<<<<<<<<<"):
        """
        Create the MRZ based on:
         - the document number
         - the date of birth
         - the expiration date
         - (optional) personal number

        @param id_pass: Document number
        @type id_pass: String (0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<)
        @param dob: Date of birth
        @type dob: String (YYMMDD)
        @param exp: Expiration date
        @type exp: String (YYMMDD)
        @param pers_num: (optional) Personal number. If not set, value = "<<<<<<<<<<<<<<"
        @type pers_num: String (0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ<)

        @return: A String "PPPPPPPPPPCXXXBBBBBBCXEEEEEECNNNNNNNNNNNNNNCC"
        """

        id_pass_full = id_pass + (9-len(id_pass))*'<' + self._calculCheckDigit(id_pass)
        dob_full = dob + self._calculCheckDigit(dob)
        exp_full = exp + self._calculCheckDigit(exp)
        pers_num_full = pers_num + self._calculCheckDigit(pers_num)
        return id_pass_full + "???" + dob_full + "?" + exp_full + pers_num_full + self._calculCheckDigit(id_pass_full+dob_full+exp_full+pers_num_full)
    
    # From pypassport > doc9303 > mrz
    def _calculCheckDigit(self, value):
        weighting = [7,3,1]
        weight = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '<':0,
          'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15, 'G':16, 'H':17, 'I':18, 'J':19, 'K':20, 'L':21, 'M':22,
          'N':23, 'O':24, 'P':25, 'Q':26, 'R':27, 'S':28, 'T':29, 'U':30, 'V':31, 'W':32, 'X':33, 'Y':34, 'Z':35};
        cpt=0
        res=0
        for x in value:
            tmp = weight[str(x)] * weighting[cpt%3]
            res += tmp            
            cpt += 1
        return str(res%10)


from passporteye import read_mrz
from passporteye.mrz.text import MRZCheckDigit
from PIL import Image
import cv2

import os, time, io, re, logging
import threading

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class OCR:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.tmp_file = 'tmp_capture.png'
        self.mrz_list = None
        self.sleep_time = .5
        self.finished = False

    def get_mrz(self):
        
        tmp_file = self.tmp_file
        mrz_list = self.mrz_list

        _, frame = self.cap.read()
        cv2.imwrite(tmp_file, frame)

        try:
            mrz = read_mrz(tmp_file)
            logging.info(mrz)
        except ValueError as e:
            logging.warning("Something went wrong...")
            return None

        print("Trying...")
        if mrz != None:
            mrz_list = [mrz.number, mrz.date_of_birth, mrz.expiration_date]
            # print("OCR: checking string [{}]".format(mrz_list))
            logging.info("OCR: checking string [{}]".format(mrz_list))

            valid_number = self.validate_doc_number(mrz.number, mrz.check_number)
            if (valid_number != None) & mrz.valid_date_of_birth & mrz.valid_expiration_date:
                mrz_list = [valid_number, mrz.date_of_birth, mrz.expiration_date]
                # print(mrz_list)

                os.remove(tmp_file)

                return mrz_list

        return None

    def end_capture(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def validate_doc_number(self, number, check_number):
        for number in self.permutations(number):
            computed_check_number = MRZCheckDigit.compute(number)
            if check_number == computed_check_number:
                return number
        
        return None

    def permutations(self, s, before="", replace="O", replace_by="0"):
        """
        This function will replace every occurance of a character or string with another character or string.
        In every possible setup, e.g. 'xxx' as input, where 'y' replaces 'x' will be return ['yxx', 'xyx', 'xxy', 'yyx', 'yxy', ... ]

        Written by Jurien Vegter in order to fix an issue where the passporteye ocr mistakes '0's for 'O's
        """
        if len(s) == len(before):
            result = []
        elif replace in s[len(before):]:
            pattern = r'(^{before}[^{replace}]*)({replace})(.*$)'.format(before=before, replace=replace)
            replaced = re.sub(pattern, r'\1[]\3', s).replace("[]", replace_by)
            result = [s, replaced]
            before = re.sub(pattern, r'\1', s)
            result.extend(self.permutations(s, before + replace, replace, replace_by))
            result.extend(self.permutations(replaced, before + replace_by, replace, replace_by))
        else:
            result = [s]

        return result
    
    def find_mrz(self):
        time.sleep(3)
        while True:
            res = self.get_mrz()

            if res:
                self.finished = True
                logging.info("Result: {}".format(res))
                break
                
            time.sleep(self.sleep_time)
        
        self.end_capture()

    def webcam(self):
        while True:
            if self.finished:
                break

            ret, frame = self.cap.read()
            cv2.imshow('webcam', frame)

            c = cv2.waitKey(1)
            if c == 27:
                break
        
        self.end_capture() 

# print(permutations(""))
# print(permutations("aObOcOd", "", "b", "XYZ"))
# print(permutations("NOHFO7F71"))

ocr = OCR()

webcam_thread = threading.Thread(name='webcam', target=ocr.webcam)
mrz_thread = threading.Thread(name='mrz', target=ocr.find_mrz)

webcam_thread.start()
mrz_thread.start()
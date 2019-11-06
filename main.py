# Classes
from session import OnboardingSession, SessionStatus
from socketio import SocketCom
from mrtd import MRTD
# Helpers
import zenroom_buffer
import image_handler
from ocr import OCR
# Config
import config
# Core
import os, json, time, logging, sys, getopt
from threading import Event, Thread

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class Main:
    def __init__(self):
        self.api_url = config.SERVER_CONFIG['prod']

        with open('zenroom/encrypt_message.lua', 'r') as input:
            self.encryption_script = input.read()

        self._init_fields()


    def _init_fields(self):
        self.session = None

        self.ocr = OCR()
        self.reader = None
        self.mrtd = None
        self.mrz = None
        self.mrtd_data = None
        self.public_key = None
        self.encrypted_data = None

        self.personal_data = None
        self.portrait_image = None

        self.i = 0

    def start(self):
        """
        1) Setup session & import Zencode script
        """
        api_url = self.api_url

        logging.info("MRTD: Connecting with {}".format(api_url))
        self.session = OnboardingSession(api_url)

    def get_mrz(self):
        """
        2) Get MRZ from ID document, should become OCR
        """
        # mrz = config.MRZ_CONFIG['mrz1']

        mrz = self.ocr.get_mrz()

        return mrz

    def get_mrtd(self):
        return self.mrtd.wait_for_card()

    def wait_for_card(self, data={}):
        # wait for nfc reader to detect a card

        mrtd = None

        if mrtd is None:
            mrtd = MRTD()

        if mrtd.wait_for_card():
            print("Card detected!")
            return { "card": True }


    def read_card(self, data={}):
        mrz = self.mrz
        if mrz is None:
            logging.info("MRTD: Trying to read MRZ...")
            mrz = self.get_mrz()

            if mrz:
                logging.info("MRTD: MRZ received [{}]".format(mrz))
                self.ocr.end_capture()
                self.mrtd = MRTD(mrz)
                self.mrz = mrz
        
        else:
            logging.info("MRTD: Waiting for card...")
            if self.get_mrtd():
                return { "mrtd": True }
        
    def setup_mrtd(self):
        """
        3) Setup MRTD and get data
        """
        output_file = False
        id_card = MRTD(self.mrz, output_file)
        
        personal_data = id_card.personal_data()

        if personal_data == None:
            logging.error("DG1 could not be read")
            return False

        image_base64 = id_card.photo_data()

        if image_base64 == None:
            logging.error("DG2 could not be read")
            return False

        self.mrtd_data = [ {'personal_data': personal_data}, {'image_base64': image_base64} ]

    def read_data(self, data={}):
        mrtd = self.mrtd

        if self.personal_data is None:
            logging.info("MRTD: Reading DG1 (personal data)...")
            self.personal_data = mrtd.personal_data()
        
        else:
            logging.info("MRTD: Reading DG2 (portrait image)...")
            portrait_image = mrtd.photo_data()

            self.mrtd_data = [ {'personal_data': self.personal_data}, {'image_base64': portrait_image} ]

            # self.show_qr()

            # qr_file = image_handler.get_qr("https://decode.amsterdam/onboarding?id=", self.session.session_id)
            qr_file = image_handler.get_qr("", self.session.session_id)

            return { 'qrcode': qr_file }

    def test_loop(self):
        self.i += 1

        if self.i is 10:
            self.i = 0
            return True

    def reset_loop(self, data={}):
        self.i += 1

        if self.i is 6:
            logging.info("MRTD: Resetting...")
            self._init_fields()
            self.start()
            return { "reset": True }


    def show_qr(self):
        """
        4) Show QR code with session ID
        """
        logging.info("Displaying QR code & waiting session status update")
        image_handler.qr_image(self.session.session_id)

        # self.ready.wait()

    def wait_for_pkey(self, data={}):
        status = self.session.get_status()

        logging.info("MRTD: Session status is [{}]".format(status))
        if status == "GOT_PUB_KEY":
            self.get_pkey()
            return { "got_pkey": True }

    def get_pkey(self):
        """
        5) Retrieve public key from session
        """
        session_data = self.session.get_data()
        p_key = session_data['data']['public_key']
        self.public_key = {'public': p_key}

    def encrypt_data(self):
        """
        6) Encrypt data with public key
        """
        # for test purposes
        # self._save_data(self.mrtd_data)

        self.encrypted_data = zenroom_buffer.execute(self.encryption_script, json.dumps(self.public_key), json.dumps(self.mrtd_data))

    def wait_for_encryption(self, data={}):
        if self.encrypted_data is None:
            self.encrypt_data()
            self.attach_data()
        
        else:
            if self.i is 2:
                self.i = 0
                return { "data_encrypted": True }
            
            self.i += 1

    def _save_data(self, data):
        """
        6.2) Save encrypted data for testing purposes
        """
        with open('output/test_data.json', 'w') as output:
            json.dump(data, output)

    def attach_data(self):
        """
        7) Add encrypted data to session
        """
        self.session.attach_encrypted_data(self.encrypted_data)

# Classes
from session import OnboardingSession
from socketio import SocketCom
from mrtd import MRTD
# Helpers
import zenroom_buffer
import image_handler
import ocr
# Config
import config
# Core
import os, json, time, logging, sys, getopt
from threading import Event

class Main:
    def start(self, api_url):
        """
        1) Setup session & import Zencode script
        """
        # api_url = config.SERVER_CONFIG['api_url']
        logging.info("Connecting with: {}".format(api_url))
        self.session = OnboardingSession(api_url)

        self.ready = Event()
        self.socket_com = SocketCom(self.ready, api_url)
        self.socket_com.join_room(self.session.session_id)

        with open('zenroom/encrypt_message.lua', 'r') as input:
            self.encryption_script = input.read()
        
        self._get_mrz()
        self._show_qr()

    def _get_mrz(self):
        """
        2) Get MRZ from ID document, should become OCR
        """
        # self._setup_mrtd(config.MRZ_CONFIG['mrz1'])

        logging.info("Reading MRZ with OCR...")
        mrz = ocr.get_mrz()
        logging.info("MRZ read [{}]".format(mrz))
        self._setup_mrtd(mrz)

    def _setup_mrtd(self, mrz):
        """
        3) Setup MRTD and get data
        """
        id_card = MRTD(mrz, True)
        
        self.personal_data = id_card.personal_data()

        if self.personal_data == None:
            sys.exit(1)

        self.image_base64 = id_card.photo_data()

        if self.image_base64 == None:
            sys.exit(1)

        # print(self.personal_data)

    def _show_qr(self):
        """
        4) Show QR code with session ID
        """
        logging.info("Displaying QR code & waiting session status update")
        image_handler.qr_image(self.session.session_id)

        self.ready.wait()
        self._get_pkey()

    def _get_pkey(self):
        """
        5) Retrieve public key from session
        """
        session_data = self.session.get_data()
        public_key = session_data['data']['public_key']
        external_public_key = {'public': public_key}

        self._encrypt_data(external_public_key)

    def _encrypt_data(self, public_key):
        """
        6) Encrypt data with public key
        """
        data_to_encrypt = []
        data_to_encrypt.append({'personal_data': self.personal_data})
        data_to_encrypt.append({'image_base64': self.image_base64})

        # for test purposes
        self._save_data(data_to_encrypt)

        data = zenroom_buffer.execute(self.encryption_script, json.dumps(public_key), json.dumps(data_to_encrypt))
        
        self._attach_data(data)

    def _save_data(self, data):
        """
        6.2) Save encrypted data for testing purposes
        """
        with open('output/test_data.json', 'w') as output:
            json.dump(data, output)

    def _attach_data(self, data):
        """
        7) Add encrypted data to session
        """
        self.session.attach_encrypted_data(data)
        
        logging.info("Done, closing!")


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

# print(str(sys.argv))

api_url = config.SERVER_CONFIG['prod']

arg = str(sys.argv)[13:][:5]
# print(arg)
if arg == "--dev":
    api_url = config.SERVER_CONFIG['dev']

# print(api_url)

main = Main()
main.start(api_url)

# main._get_mrz()
from Tkinter import *
from mrtd import MRTD
import json

class GUI:
    def __init__(self, master):
        self.master = master
        self.photo = None
        self.default_data = True

        master.title("MRTD Reader")

        column2width=30

        # Label(master, text="MRZ:").grid(row=0, column=0, pady=5, padx=5, sticky=E)
        # self.mrzEntry = Entry(master, width=column2width)
        # self.mrzEntry.grid(row=0, column=1, pady=5, padx=5)
        # self.mrzEntry.focus_set()

        Label(master, text="Document number:").grid(row=1, column=0, pady=5, padx=5, sticky=E)
        self.docNrEntry = Entry(master, width=column2width)
        self.docNrEntry.grid(row=1, column=1, pady=5, padx=5, sticky=W)

        Label(master, text="Date of birth:").grid(row=2, column=0, pady=5, padx=5, sticky=E)
        self.dobEntry = Entry(master, width=column2width)
        self.dobEntry.grid(row=2, column=1, pady=5, padx=5, sticky=W)

        Label(master, text="Expiry date:").grid(row=3, column=0, pady=5, padx=5, sticky=E)
        self.expDateEntry = Entry(master, width=column2width)
        self.expDateEntry.grid(row=3, column=1, pady=5, padx=5, sticky=W)

        self.default_data_check = Checkbutton(master, text="Use dev data", variable=self.default_data)
        self.default_data_check.grid(row=4, column=0, pady=5, padx=5, sticky=E)

        self.get_data_button = Button(master, text="Get data", command=self.get_data)
        self.get_data_button.grid(row=4, column=1, pady=5, padx=5, sticky=E)

    def get_data(self):
        
        if self.default_data:
            with open('config.json') as input:
                json_input = json.load(input)
                docNumber = json_input['docNumber']
                self.docNrEntry.insert(0, docNumber)
                dateOfBirth = json_input['dob']
                self.dobEntry.insert(0, dateOfBirth)
                expiryDate = json_input['expDate']
                self.expDateEntry.insert(0, expiryDate)

        docNumber = self.docNrEntry.get()
        dateOfBirth = self.dobEntry.get()
        expiryDate = self.expDateEntry.get()

        mrz = [docNumber, dateOfBirth, expiryDate]
        
        id = MRTD(mrz, False)

        personal_data = id.personal_data()

        image_base64 = id.photo_data('png')
        self.set_output(personal_data, image_base64)
    
    def set_output(self, personal_data, image_base64):
        self.photo = PhotoImage(data=image_base64)
        self.photoImage = Label(self.master, image=self.photo)
        self.photoImage.grid(row=5, column=1, pady=5, padx=5, sticky=W)

        Label(self.master, text=personal_data['Name of Holder']).grid(row=6, column=1, pady=5, padx=5, sticky=(W, N))
        Label(self.master, text=personal_data['Sex']).grid(row=7, column=1, pady=5, padx=5, sticky=(W, N))
        Label(self.master, text=personal_data['Nationality']).grid(row=8, column=1, pady=5, padx=5, sticky=(W, N))
        Label(self.master, text=personal_data['Document Type']).grid(row=9, column=1, pady=5, padx=5, sticky=(W, N))

root = Tk()
gui = GUI(root)
root.mainloop()
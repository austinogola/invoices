from __future__ import print_function
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import os.path
from googleapiclient.http import MediaFileUpload

DOC_SCOPES = ['https://www.googleapis.com/auth/documents']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

SERVICE_ACCOUNT_FILE = 'keys.json'

drive_creds = None
docs_creds = None

drive_creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=DRIVE_SCOPES)

docs_creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=DOC_SCOPES)


doc_service = build('docs', 'v1', credentials=docs_creds)
drive_service=build('drive', 'v3', credentials=drive_creds)

def execute(invoice,client,services,charges):

    invoice_number=invoice['number']
    invoice_date=invoice['date']

    client_name=client['name']
    client_location=client['location']
    client_phone=client['phone']
    client_email=client['email']

    service_type=service['type']
    service_date=service['date']
    service_items=service['items']

    subtotal=get_subtotal()
    tax_rate=charges['tax_rate']
    other_charges=charges['other charges']
    total



    #fetch invoice template
    files=drive_service.files().list(q="name = 'invoice' ").execute()
    item=files.get("files",[])
    invoice_id=item[0]['id']

    #Copy invoice
    respo=drive_service.files().copy(fileId=invoice_id).execute()
    copy_id=respo.get('id')

    #Fill invoice(Update copy)
    single_slots=[
        '<<invoice no.>>','<<invoice_date>>',"<<client_name>>",'<<client_location>>','<<client_phone>>',
        '<<service_type>>','<<service_date>>','<<subtotal>>',"<<tax rate>>",'<<other charges>>','<<total>>'
        ]
    single_entries=[]
    reqs=[]
    for slot,index in single_slots:
        reqs.append({
            'replaceAllText':{
                'containsText':{
                    "text":f"{slot}",
                    "matchCase":True
                    },
                "replaceText":single_entries[index]
                }
        })
    
    #Rename the file to its id

    #Move file to Invoices folder

    #Arrange file 

def get_subtotal():
    print(subtotal)




    








# if not items:
#     print('No items found')
# else:
#     for item in items:
#         print(f'{item["name"]}')


#Templating
reqs=[]
reqs.append({
    'replaceAllText':{
        'containsText':{
            "text":"<<client_name>>",
            "matchCase":True
        },
        "replaceText":"Austin Ogola"
    }
})

req_body={"requests":reqs}
result=documents()

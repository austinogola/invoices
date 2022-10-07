from __future__ import print_function
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import os.path
from googleapiclient.http import MediaFileUpload
import calendar

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

def execute(invoice,client,service,charges):

    invoice_number=invoice['number']
    invoice_date=invoice['date']

    client_name=client['name']
    client_location=client['location']
    client_phone=client['phone']
    client_email=client['email']

    service_type=service['type']
    service_date=service['date']
    service_items=service['items']

    all_data=[invoice_number,invoice_date,client_name,client_location,client_phone,client_email,service_type,
    service_date]

    # service_items=service['items']

    # subtotal=get_subtotal()
    # tax_rate=charges['tax_rate']
    # other_charges=charges['other charges']
    # total



    #fetch invoice template
    template_id=get_template_id()


    #Copy invoice template
    respo=drive_service.files().copy(fileId=template_id).execute()
    copy_id=respo.get('id')


    #Fill invoice(Update copy)
    fill_template(all_data,copy_id)
    
    
    #Rename the file to its id
    rename(copy_id,invoice_number)

    files=drive_service.files().list(q="name = 'Invoices' ").execute()
    Invoices=files.get("files",[])
    folder_id=Invoices[0]['id']
    


    #Create month folder if none
    months = {
        '1':'Jan','2':'Feb','3': 'Mar', '4':'Apr', '5':'May','6': 'Jun', 
        '7':'Jul','8':'Aug','9':'Sep','10':'Oct', "11": 'Nov', "12":'Dec'}

    month=months[f'service_date.split('/')[2]']
    

    month_folders=drive_service.files().list(
        q="mimeType = 'application/vnd.google-apps.folder' and name = f'{month}'")
    
    if not month_folders.get('files',[]):
        folder_metadata = {
            'name': f'{month}',
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = drive_service.files().create(body=folder_metadata,fields='id').execute()
    
    #Create date folder if none
    date=service_date.split('/')[0]
    date_folders=drive_service.files().list(
        q="mimeType = 'application/vnd.google-apps.folder' and name = f'{month}'")
    
    if not date_folders.get('files',[]):
        folder_metadata = {
            'name': f'{date}',
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = drive_service.files().create(body=folder_metadata,fields='id').execute()
    


    


    #Create date folder if none


    #Move file to date folder
    move_copy(copy_id)




    #Arrange file 



def get_template_id():
    files=drive_service.files().list(q="name = 'invoice' ").execute()
    item=files.get("files",[])
    invoice_id=item[0]['id']
    return (invoice_id)

def fill_template(entries,copy_id):
    single_slots=[
        '<<invoice no.>>','<<invoice_date>>',"<<client_name>>",'<<client_location>>','<<client_phone>>',
        '<<client_email>>','<<service_type>>','<<service_date>>']

    reqs=[]
    for index,slot in enumerate(single_slots):
        reqs.append({
            'replaceAllText':{
                'containsText':{
                    "text":f"{slot}",
                    "matchCase":True
                    },
                "replaceText":entries[index]
                }
        })
    
    result=doc_service.documents().batchUpdate(documentId=copy_id,body={'requests':reqs}).execute()


def rename(copy_id,new_name):
    rename_file = {'name': new_name}

    updated_file = drive_service.files().update(
        fileId=copy_id,
        body=rename_file).execute()

    
    print(updated_file)

# def get_subtotal():
#     print(subtotal)

def move_copy(copy_id,folder_id):
    # parents = drive_service.parents().list(fileId=copy_id).execute()
    # prev_parent=parents['items'][0]['id']

    # # m_file=drive_service.get(fileId=copy_id,fields='parents').execute()
    # # previous_parent=",".join(m_file.get('parents'))

    
    # moved_file=drive_service.parents().insert(fileId=copy_id,body={'id':folder_id}).execute()
    # rmv_from_prv=drive_service.parents().delete(fileId=copy_id, parentId=prev_parent).execute()

    # # moved_file=drive_service.files().update(
    # #     fileId=copy_id ,addParents=folder_id, removeParents=previous_parent, fields='id, parents').execute()

    # print(moved_file)

    m_file = drive_service.files().get(fileId=copy_id, fields='parents').execute()
    previous_parents = ",".join(m_file.get('parents'))


    
    file = drive_service.files().update(fileId=copy_id, addParents=folder_id,
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()
    print(file.get('parents'))
    # parent=drive_service.files().get(fileId=copy_id).execute()
    # print (parent)



    








# if not items:
#     print('No items found')
# else:
#     for item in items:
#         print(f'{item["name"]}')


#Templating
# reqs=[]
# reqs.append({
#     'replaceAllText':{
#         'containsText':{
#             "text":"<<client_name>>",
#             "matchCase":True
#         },
#         "replaceText":"Austin Ogola"
#     }
# })

# req_body={"requests":reqs}
# result=documents()

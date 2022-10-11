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

    # subtotal=get_subtotal()
    # tax_rate=charges['tax_rate']
    # other_charges=charges['other charges']
    # total



    #fetch invoice template
    files=drive_service.files().list(q='name = "invoice" ').execute()
    items=files.get('files',[])
    template_id=items[0]['id']
    print('Fetched template')


    #Copy invoice template
    respo=drive_service.files().copy(fileId=template_id).execute()
    copy_id=respo.get('id')


    #Fill invoice(Update copy)
    fill_template(all_data,copy_id)
    print('Template filled')

    fill_services(service_items,copy_id)
    
    
    #Rename the file to its invoice number
    rename(copy_id,invoice_number)
    print('Copy renamed')

    
    folder_id=get_id('Invoices')

    

    date=split_date(invoice_date)
    year=date['year']
    month=date['month']
    day=date['day']

    #create months and dates folders if none
    date_folder_id=handle_folders(day, month, year)
    print('date folder created')


    #Move file to date folder
    move_copy(copy_id,date_folder_id)
    print('copy moved to date folder')

    return 'Successfull'





def get_template_id():
    return (get_id('invoice'))

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
    
    # parent=drive_service.files().get(fileId=copy_id).execute()
    # print (parent)

def get_id(name):
    query=f'name = "{name}"'
    files=drive_service.files().list(q=query).execute()
    items=files.get('files',[])

    if items:
        return items[0]['id']
    else:
        return None 


def split_date(date):
    months = {
        '1':'Jan','2':'Feb','3': 'Mar', '4':'Apr', '5':'May','6': 'Jun', 
        '7':'Jul','8':'Aug','9':'Sep','10':'Oct', "11": 'Nov', "12":'Dec'}

    date_arr=date.split('/')
    day=date_arr[0]
    month_number=date_arr[1]

    year=date_arr[2]
    month=months[month_number]
    
    return ({"day":day,"month":month,'year':year})



def handle_folders(day,month,year):
    Invoices_folder=get_id('Invoices')

    year_id=handle_year(year)
    month_id=handle_month(month,year)
    day_id=handle_day(day, month_id)

    return day_id

    

def handle_year(year):
    Invoices_folder=get_id('Invoices')

    year_id=get_id(year)
    if not year_id:

        folder_metadata = {
            'name': f'{year}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':[Invoices_folder]
        }
        folder = drive_service.files().create(body=folder_metadata,fields='id').execute()
    

    year_id=get_id(year)

    return (year_id)

def handle_month(month,year):
    year_folder=get_id(year)

    month_id=get_id(month)
    if not month_id:

        folder_metadata = {
            'name': f'{month}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':[year_folder]
        }
        folder = drive_service.files().create(body=folder_metadata,fields='id').execute()
    

    month_id=get_id(month)

    return (month_id)

def handle_day(day,month_id):

    day_id=get_id(day)
    if not day_id:

        folder_metadata = {
            'name': f'{day}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':[month_id]
        }
        folder = drive_service.files().create(body=folder_metadata,fields='id').execute()
    

    day_id=get_id(day)

    return (day_id)

def fill_services(services,copy_id):
    print('aaa')

def create_table():
    Invoices_folder=get_id('Invoices')

    files=drive_service.files().list(q='name = "invoice2" ').execute()
    items=files.get('files',[])
    template_id=items[0]['id']

    respo=drive_service.files().copy(fileId=template_id).execute()
    copy_id=respo.get('id')

    # requests=[{
    #     'insertTable':{
    #         'rows': 1,
    #         'columns': 3,
    #         'endOfSegmentLocation': {
    #             'segmentId': 'services'
    #       }
    #     }
    # }]

    requests=[{
        'insertText':{
            'location':{
                "index":323
            },
            'text':'\nThis is the text to insert'
        }
    }]

    result = doc_service.documents().batchUpdate(documentId=copy_id, body={'requests': requests}).execute()

    rename(copy_id,'trial10.pdf')

    move_copy(copy_id,Invoices_folder)


create_table()





    


    








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

import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.Certificate('fstore_keys.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()

def add_to_store(invoice,client,service,charges):
    
    invoice_number=invoice['number']
    invoice_date=invoice['date']

    client_names=client['name'].split(' ')
    client_location=client['location']
    # client_phone=client['phone']
    client_email=client['email']

    client={
        "email":client_email,
        "fname":client_names[0],
        "lname":client_names[1],
        "location":client_location
    }

    service_type=service['type']
    service_date=service['date']
    service_items=service['items']

    tax_rate=charges['tax_rate']
    other_charges=charges['other charges']

    data={
        "client":client,
        "service":service,
        "charges":charges
    }

    


    # doc_ref = db.collection(u'invoices').document(f'{str(invoice_number)}')
    doc_ref = db.collection(u'invoices').document().set(data)
    print('Invoice successfully added to store')
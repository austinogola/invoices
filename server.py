from flask import Flask,jsonify,request
from main import execute

app=Flask(__name__)

@app.route('/invoice',methods=['POST','GET'])
def invoice():
    data=request.json
    invoice=data['invoice']
    client=data['client']
    service=data['service']
    charges=data['charges']

    print(invoice,client,service,charges)

    execute(invoice,client,service,charges)

    return ('Successful')
    



app.run(port=3000)

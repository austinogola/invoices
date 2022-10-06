from flask import Flask,jsonify,request

app=Flask(__name__)

@app.route('/invoice',methods=['POST','GET'])
def invoice():
    data=request.json
    invoice=data['invoice']
    client=data['client']
    service=data['service']
    charges=data['charges']

    print(invoice,client)

    return (invoice,client,service)
    



app.run(port=3000)

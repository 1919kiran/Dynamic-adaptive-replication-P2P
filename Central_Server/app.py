from flask import (
    Flask, 
    jsonify,
    request
)

app = Flask(__name__)
file_to_node = {}
node_to_IP = {}
@app.route('/requestfile',methods=["GET","POST"])
def index():
    data = request.get_json() # parses JSON request data
    file = data.get('file') 
    # for node in file_to_node[file]:
        #find_overheating
    
    # response = requests.post('http:', json=payload, headers=headers)
    return "Requested "

@app.route('/addfiles',methods=["GET","POST"])
def files():
    data = request.get_json() 
    print(data)
    file_to_node = data
    print(file_to_node)
    return "done"

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug =True,port=5001)
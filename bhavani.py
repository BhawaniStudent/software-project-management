from flask import Flask, render_template_string, request, jsonify
import hashlib, json
from time import time
from uuid import uuid4
import os

# ---------------- Blockchain Logic ----------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

# ---------------- Flask App ----------------
app = Flask(__name__)  # ✅ Must be top-level
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

# ---------------- HTML Page ----------------
page = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Blockchain Web App</title>
    <style>
        body { font-family: Arial; background:#f5f5f5; text-align:center; margin:20px;}
        button { padding:10px 20px; margin:5px; border:none; border-radius:6px; cursor:pointer;}
        #mine { background:#28a745; color:white; }
        #showChain { background:#007bff; color:white; }
        #addTx { background:#ffc107; color:black; }
        #output { margin-top:20px; text-align:left; width:80%; margin:auto; background:white; padding:10px; border-radius:8px; max-height:500px; overflow:auto;}
        input { padding:5px; margin:5px; }
        .block { border:1px solid #333; padding:10px; margin:5px; border-radius:5px; background:#eef; }
    </style>
</head>
<body>
    <h1>🪙 Python Blockchain Web Application</h1>

    <button id="mine" onclick="mineBlock()">⛏️ Mine New Block</button>
    <button id="showChain" onclick="showChain()">🔗 Show Blockchain</button>

    <div>
        <h3>Add Transaction</h3>
        <input id="sender" placeholder="Sender">
        <input id="recipient" placeholder="Recipient">
        <input id="amount" placeholder="Amount">
        <button id="addTx" onclick="addTransaction()">Add</button>
    </div>

    <div id="output">Output will appear here...</div>

<script>
function addTransaction(){
    let sender = document.getElementById('sender').value;
    let recipient = document.getElementById('recipient').value;
    let amount = document.getElementById('amount').value;
    fetch('/transactions/new', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({sender,recipient,amount})
    }).then(r=>r.json()).then(data=>{
        document.getElementById('output').innerHTML = `<p>${data.message || data.error}</p>`;
    });
}

function mineBlock(){
    fetch('/mine').then(r=>r.json()).then(block=>{
        let output = document.getElementById('output');
        let html = `<h3>New Block Mined!</h3>`;
        html += `<div class="block"><b>Index:</b> ${block.index} <br>`;
        html += `<b>Timestamp:</b> ${new Date(block.timestamp*1000).toLocaleString()} <br>`;
        html += `<b>Transactions:</b><br>`;
        block.transactions.forEach(tx => {
            html += `&nbsp;&nbsp;${tx.sender} → ${tx.recipient} : ${tx.amount} <br>`;
        });
        html += `<b>Proof:</b> ${block.proof} <br>`;
        html += `<b>Previous Hash:</b> ${block.previous_hash} <br></div>`;
        output.innerHTML = html;
    });
}

function showChain(){
    fetch('/chain').then(r=>r.json()).then(data=>{
        let output = document.getElementById('output');
        let html = `<h3>Full Blockchain</h3>`;
        data.chain.forEach(block => {
            html += `<div class="block"><b>Index:</b> ${block.index} <br>`;
            html += `<b>Timestamp:</b> ${new Date(block.timestamp*1000).toLocaleString()} <br>`;
            html += `<b>Transactions:</b><br>`;
            block.transactions.forEach(tx => {
                html += `&nbsp;&nbsp;${tx.sender} → ${tx.recipient} : ${tx.amount} <br>`;
            });
            html += `<b>Proof:</b> ${block.proof} <br>`;
            html += `<b>Previous Hash:</b> ${block.previous_hash} <br></div>`;
        });
        output.innerHTML = html;
    });
}
</script>
</body>
</html>
"""

# ---------------- Flask Routes ----------------
@app.route('/')
def home():
    return render_template_string(page)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    if not values or not all(k in values for k in ['sender', 'recipient', 'amount']):
        return jsonify({'error': 'Missing values'}), 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    return jsonify({'message': f'Transaction will be added to Block {index}'})

@app.route('/mine')
def mine():
    last_block = blockchain.last_block
    proof = 100  # simplified proof
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    block = blockchain.new_block(proof)
    return jsonify(block)

@app.route('/chain')
def full_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)})

# ---------------- Run Flask ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)


# Connect to the database
def connect_to_db():
    try:
        conn = pyodbc.connect("Driver={SQL Server};Server=Angel\\MSSQLSERVER04;Database=data;")
    
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Routes

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.json
    if not data or 'name' not in data or 'email' not in data or 'mobile' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    conn = connect_to_db()
    if not conn:
        return jsonify({'error': 'Failed to connect to database'}), 500

    cursor = conn.cursor()
    cursor.execute("INSERT INTO User (name, email, mobile) VALUES (?, ?, ?)", (data['name'], data['email'], data['mobile']))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/expense', methods=['POST'])
def add_expense():
    data = request.json
    if not data or 'amount' not in data or 'user_id' not in data or 'expense_type' not in data or 'participants' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    conn = connect_to_db()
    if not conn:
        return jsonify({'error': 'Failed to connect to database'}), 500

    cursor = conn.cursor()
    cursor.execute("INSERT INTO Expense (amount, user_id, expense_type) VALUES (?, ?, ?)", (data['amount'], data['user_id'], data['expense_type']))
    expense_id = cursor.lastrowid

    for participant_id in data['participants']:
        cursor.execute("INSERT INTO ExpenseParticipant (expense_id, user_id) VALUES (?, ?)", (expense_id, participant_id))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Expense added successfully'}), 201

@app.route('/api/balance/<int:user_id>')
def get_balance(user_id):
    conn = connect_to_db()
    if not conn:
        return jsonify({'error': 'Failed to connect to database'}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ExpenseParticipant WHERE user_id = ?", (user_id,))
    balances = {}
    for row in cursor.fetchall():
        expense_id, participant_id = row
        if participant_id != user_id:
            cursor.execute("SELECT amount FROM Expense WHERE id = ?", (expense_id,))
            amount = cursor.fetchone()[0]
            balances[participant_id] = balances.get(participant_id, 0) + amount

    conn.close()

    return jsonify({'user_id': user_id, 'balances': balances})

if __name__ == '__main__':
    app.run(debug=True)

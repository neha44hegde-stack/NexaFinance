from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import date, timedelta

app = Flask(__name__)
import os
db_url = os.environ.get('DATABASE_URL', 'sqlite:///finance.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, resources={r'/api/*': {'origins': ['https://nexafinance-1.onrender.com', 'http://localhost:5000', 'http://127.0.0.1:5000']}})

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False) # income/expense
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=date.today)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    saved_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    outstanding_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    monthly_emi = db.Column(db.Float, nullable=False)
    total_tenure = db.Column(db.Integer, nullable=False)
    remaining_tenure = db.Column(db.Integer, nullable=False)
    next_payment_date = db.Column(db.Date)

# NEW: Recurring Expense
class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    frequency = db.Column(db.String(20), default='monthly') # weekly, monthly, yearly
    next_due_date = db.Column(db.Date, default=date.today)

# NEW: Asset (for Net Worth)
class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

# --- Auth Routes ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username exists'}), 400
    u = User(username=data['username'], email=data['email'], password_hash=generate_password_hash(data['password']))
    db.session.add(u); db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    u = User.query.filter_by(username=data['username']).first()
    if u and check_password_hash(u.password_hash, data['password']):
        return jsonify({'access_token': create_access_token(identity=str(u.id))}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# --- Transactions (Income/Expenses) ---
@app.route('/api/transactions', methods=['GET', 'POST'])
@jwt_required()
def transactions():
    uid = get_jwt_identity()
    if request.method == 'GET':
        txns = Transaction.query.filter_by(user_id=uid).order_by(Transaction.date.desc()).all()
        return jsonify([{'id': t.id, 'type': t.type, 'amount': t.amount, 'category': t.category, 'description': t.description, 'date': str(t.date)} for t in txns])
    data = request.get_json()
    t = Transaction(user_id=uid, type=data['type'], amount=data['amount'], category=data.get('category','Other'), description=data.get('description',''), date=date.fromisoformat(data['date']))
    db.session.add(t); db.session.commit()
    return jsonify({'message': 'Added', 'id': t.id}), 201

@app.route('/api/transactions/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_transaction(id):
    uid = get_jwt_identity()
    t = Transaction.query.filter_by(id=id, user_id=uid).first()
    if not t: return jsonify({'message': 'Not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        t.amount = data.get('amount', t.amount); t.category = data.get('category', t.category)
        t.description = data.get('description', t.description); t.date = date.fromisoformat(data.get('date', str(t.date)))
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    db.session.delete(t); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# --- Budgets ---
@app.route('/api/budgets', methods=['GET', 'POST'])
@jwt_required()
def budgets():
    uid = get_jwt_identity()
    if request.method == 'GET':
        return jsonify([{'id': b.id, 'category': b.category, 'amount': b.amount, 'month': b.month, 'year': b.year} for b in Budget.query.filter_by(user_id=uid).all()])
    data = request.get_json()
    b = Budget(user_id=uid, category=data['category'], amount=data['amount'], month=data.get('month', date.today().month), year=data.get('year', date.today().year))
    db.session.add(b); db.session.commit()
    return jsonify({'message': 'Added', 'id': b.id}), 201

@app.route('/api/budgets/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_budget(id):
    uid = get_jwt_identity()
    b = Budget.query.filter_by(id=id, user_id=uid).first()
    if not b: return jsonify({'message': 'Not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        b.amount = data.get('amount', b.amount); b.category = data.get('category', b.category)
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    db.session.delete(b); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# --- Savings Goals ---
@app.route('/api/savings-goals', methods=['GET', 'POST'])
@jwt_required()
def savings_goals():
    uid = get_jwt_identity()
    if request.method == 'GET':
        return jsonify([{'id': g.id, 'name': g.name, 'target_amount': g.target_amount, 'saved_amount': g.saved_amount, 'deadline': str(g.deadline) if g.deadline else None} for g in SavingsGoal.query.filter_by(user_id=uid).all()])
    data = request.get_json()
    g = SavingsGoal(user_id=uid, name=data['name'], target_amount=data['target_amount'], saved_amount=data.get('saved_amount', 0.0), deadline=date.fromisoformat(data['deadline']) if data.get('deadline') else None)
    db.session.add(g); db.session.commit()
    return jsonify({'message': 'Added', 'id': g.id}), 201

@app.route('/api/savings-goals/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_savings_goal(id):
    uid = get_jwt_identity()
    g = SavingsGoal.query.filter_by(id=id, user_id=uid).first()
    if not g: return jsonify({'message': 'Not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        g.name = data.get('name', g.name); g.target_amount = data.get('target_amount', g.target_amount)
        g.saved_amount = data.get('saved_amount', g.saved_amount)
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    db.session.delete(g); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# --- Loans ---
@app.route('/api/loans', methods=['GET', 'POST'])
@jwt_required()
def loans():
    uid = get_jwt_identity()
    if request.method == 'GET':
        return jsonify([{'id': l.id, 'name': l.name, 'principal_amount': l.principal_amount, 'outstanding_amount': l.outstanding_amount, 'interest_rate': l.interest_rate, 'monthly_emi': l.monthly_emi, 'total_tenure': l.total_tenure, 'remaining_tenure': l.remaining_tenure, 'next_payment_date': str(l.next_payment_date) if l.next_payment_date else None} for l in Loan.query.filter_by(user_id=uid).all()])
    data = request.get_json()
    l = Loan(user_id=uid, name=data['name'], principal_amount=data['principal_amount'], outstanding_amount=data.get('outstanding_amount', data['principal_amount']), interest_rate=data.get('interest_rate', 0.0), monthly_emi=data['monthly_emi'], total_tenure=data['total_tenure'], remaining_tenure=data.get('remaining_tenure', data['total_tenure']), next_payment_date=date.fromisoformat(data['next_payment_date']) if data.get('next_payment_date') else date.today())
    db.session.add(l); db.session.commit()
    return jsonify({'message': 'Added', 'id': l.id}), 201

@app.route('/api/loans/<int:id>/pay-emi', methods=['POST'])
@jwt_required()
def pay_emi(id):
    uid = get_jwt_identity()
    l = Loan.query.filter_by(id=id, user_id=uid).first()
    if not l: return jsonify({'message': 'Not found'}), 404
    if l.remaining_tenure <= 0: return jsonify({'message': 'Already paid'}), 400
    l.outstanding_amount = max(0, l.outstanding_amount - l.monthly_emi)
    l.remaining_tenure -= 1
    if l.next_payment_date: l.next_payment_date = l.next_payment_date + timedelta(days=30)
    db.session.commit()
    return jsonify({'message': 'EMI paid'}), 200

@app.route('/api/loans/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_loan(id):
    uid = get_jwt_identity()
    l = Loan.query.filter_by(id=id, user_id=uid).first()
    if not l: return jsonify({'message': 'Not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        l.name = data.get('name', l.name); l.monthly_emi = data.get('monthly_emi', l.monthly_emi); l.remaining_tenure = data.get('remaining_tenure', l.remaining_tenure); l.outstanding_amount = data.get('outstanding_amount', l.outstanding_amount)
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    db.session.delete(l); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# --- Recurring Expenses ---
@app.route('/api/recurring', methods=['GET', 'POST'])
@jwt_required()
def recurring():
    uid = get_jwt_identity()
    if request.method == 'GET':
        recs = RecurringExpense.query.filter_by(user_id=uid).all()
        return jsonify([{'id': r.id, 'name': r.name, 'amount': r.amount, 'category': r.category, 'frequency': r.frequency, 'next_due_date': str(r.next_due_date)} for r in recs])
    data = request.get_json()
    r = RecurringExpense(user_id=uid, name=data['name'], amount=data['amount'], category=data.get('category','Other'), frequency=data.get('frequency','monthly'), next_due_date=date.fromisoformat(data['next_due_date']) if data.get('next_due_date') else date.today())
    db.session.add(r); db.session.commit()
    return jsonify({'message': 'Added', 'id': r.id}), 201

@app.route('/api/recurring/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_recurring(id):
    uid = get_jwt_identity()
    r = RecurringExpense.query.filter_by(id=id, user_id=uid).first()
    if not r: return jsonify({'message': 'Not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        r.name = data.get('name', r.name); r.amount = data.get('amount', r.amount); r.frequency = data.get('frequency', r.frequency)
        if data.get('next_due_date'): r.next_due_date = date.fromisoformat(data['next_due_date'])
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    db.session.delete(r); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# --- Assets (Net Worth) ---
@app.route('/api/assets', methods=['GET', 'POST'])
@jwt_required()
def assets():
    uid = get_jwt_identity()
    if request.method == 'GET':
        assets = Asset.query.filter_by(user_id=uid).all()
        return jsonify([{'id': a.id, 'name': a.name, 'value': a.value} for a in assets])
    data = request.get_json()
    a = Asset(user_id=uid, name=data['name'], value=data['value'])
    db.session.add(a); db.session.commit()
    return jsonify({'message': 'Added', 'id': a.id}), 201

@app.route('/api/assets/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def edit_asset(id):
    uid = get_jwt_identity()
    a = Asset.query.filter_by(id=id, user_id=uid).first()
    if not a: return jsonify({'message': 'Not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        a.name = data.get('name', a.name); a.value = data.get('value', a.value)
        db.session.commit()
        return jsonify({'message': 'Updated'}), 200
    db.session.delete(a); db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# --- Frontend Route ---
@app.route('/')
def home():
    return send_from_directory(r'C:\Users\Admin\Sensible-Finance-Manager\expense-tracker', 'index.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)




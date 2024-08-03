from flask import Flask, request, jsonify
from app import app, db
from app.models import User  # Assuming you have a User model defined

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    language = data.get('language')

    if not email or not language:
        return jsonify({'error': 'Email and language are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    new_user = User(email=email, language=language)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User signed up successfully'}), 200

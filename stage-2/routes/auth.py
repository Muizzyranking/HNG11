from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models import Organisation, OrganisationUser, User, db
from utils.validators import validate_user_data

bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = validate_user_data(data)
    if errors:
        return jsonify({"errors": errors}), 422

    try:
        user = User(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            password=data['password'],
            phone=data['phone']
        )
        db.session.add(user)
        db.session.commit()

        org_name = f"{data['firstName']}'s Organisation"
        org = Organisation(
            name=org_name,
            description=f"This is {data['firstName']}'s Organisation",
        )
        db.session.add(org)
        db.session.commit()

        org_user = OrganisationUser(
            orgId=org.orgId,
            userId=user.userId
        )
        db.session.add(org_user)
        db.session.commit()

        access_token = create_access_token(identity=user.userId)

        response = {
            "status": "Success",
            "message": "Registeration Successful",
            "data": {
                "access_token": access_token,
                "user": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone,
                },
            },
        }
        return jsonify(response), 201

    except Exception as e:  # noqa: F841
        db.session.rollback()
        return jsonify({
            "status": "Bad Request",
            "message": "Registeration Unsuccessful",
            "statusCode": 400,
        }), 400


@bp_auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        resposnse = {
            "status": "Bad Request",
            "message": "Authentication failed",
            "statusCode": 401
        }
        return jsonify(resposnse), 401

    access_token = create_access_token(identity=user.userId)
    response = {
        "status": "Success",
        "message": "Login Successful",
        "data": {
            "access_token": access_token,
            "user": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone,
            },
        },
    }
    return jsonify(response), 200

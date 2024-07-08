from flask import Blueprint, request, jsonify
from models import db, Organisation, OrganisationUser, User
from flask_jwt_extended import jwt_required, get_jwt_identity

api_bp = Blueprint('api', __name__)


@api_bp.route('/users/<id>', methods=['GET'])
@jwt_required
def get_user(id):
    current_user_id = get_jwt_identity()

    if id == current_user_id:
        user = User.query.filter_by(userId=id).first()
        if not user:
            response = {
                "status": "Failed",
                "message": "User not found",
            }
            return jsonify(response), 404

        response = {
            "status": "Success",
            "message": "User retrieved successfully",
            "data": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone,
            }
        }
        return jsonify(response), 200

    user_orgs = Organisation.query.join(OrganisationUser).filter(
        OrganisationUser.userId == current_user_id).all()

    for org in user_orgs:
        if User.query.join(OrganisationUser).filter(
                OrganisationUser.orgId == org.orgId,
                OrganisationUser.userId == id).first():
            user = User.query.get(id)
            if not user:
                response = {
                    "status": "Failed",
                    "message": "User not found",
                }
                return jsonify(response), 404

            response = {
                "status": "Success",
                "message": "User retrieved successfully",
                "data": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone,
                }
            }
            return jsonify(response), 200

    return jsonify({
        "status": "Unauthorized",
        "message": "Access denied",
    }), 403


@api_bp.route('/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    user_id = get_jwt_identity()
    organisations = Organisation.query.join(OrganisationUser).filter(
        OrganisationUser.userId == user_id).all()
    org_list = [
        {
            "orgId": org.orgId,
            "name": org.name,
            "description": org.description,
        } for org in organisations
    ]
    response = {
        "status": "Success",
        "messae": "Organisations retrieved successfully",
        "data": {
            "organisations": org_list

        }
    }
    return jsonify(response), 200


@api_bp.route('/organisations/<id>', methods=['GET'])
@jwt_required
def get_organisation(id):
    user_id = get_jwt_identity()
    organisation = Organisation.query.join(OrganisationUser).filter(
        OrganisationUser.userId == user_id,
        OrganisationUser.orgId == id).first()
    if not organisation:
        return jsonify({
            "status": "Bad request",
            "message": "Organisation not found",
        }), 404
    response = {
        "status": "Success",
        "message": "Organisation retrieved successfully",
        "data": {
            "orgId": organisation.orgId,
            "name": organisation.name,
            "description": organisation.description,
        }
    }
    return jsonify(response), 200


@api_bp.route('/organisations', methods=['POST'])
@jwt_required
def create_organisation():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if not name or not description:
        return jsonify({
            "errors": {
                "field": "name",
                "message": "Name can not be null"
            }
        }), 400

    try:
        organisation = Organisation(name=name, description=description)
        db.session.add(organisation)
        db.session.commit()

        current_user = get_jwt_identity()
        org_user = OrganisationUser(
            orgId=organisation.orgId, userId=current_user)
        db.session.add(org_user)
        db.session.commit()

        response = {
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "orgId": organisation.orgId,
                "name": organisation.name,
                "description": organisation.description,
            }
        }
        return jsonify(response), 201
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "Bad Request",
            "message": "client error",
            "statusCode": 400,
        }), 400


@api_bp.route("/organisations/<id>/users", method=['POST'])
@jwt_required
def add_user_to_organisation(id):
    data = request.get_json()
    user_id = data.get('userId')

    if not user_id:
        return jsonify({
            "errors": {
                "field": "userId",
                "message": "userId can not be null"
            }
        }), 400

    organisation = Organisation.query.get(orgId=id)
    if not organisation:
        return jsonify({
            "status": "Bad Request",
            "message": "Organisation not found",
        }), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "Bad Request",
            "message": "User not found",
        }), 404

    org_user = OrganisationUser(orgId=id, userId=user_id)
    db.session.add(org_user)
    db.session.commit()

    response = {
        "status": "Success",
        "message": "User added to organisation successfully",
    }
    return jsonify(response), 200

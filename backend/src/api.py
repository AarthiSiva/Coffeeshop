import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

#db_drop_and_create_all()

# ROUTES

#GET /drinks 
def get_drinks_helper():
    drinks = Drink.query.order_by(Drink.id).all()
    if(len(drinks)==0):
        abort(404)
    drinks_short =[]
    for drink in drinks:
        drinks_short.append(drink.short())

    return jsonify(
            {
                'success':True,
                'drinks':drinks_short
            }
        )

@app.route('/drinks', methods=['GET'])
def get_drinks():
    return get_drinks_helper()


#GET /drinks-detail
def get_drinks_detail_helper():
    drinks = Drink.query.order_by(Drink.id).all()
    if(len(drinks)==0):
        abort(404)
    drinks_long =[]
    for drink in drinks:
        drinks_long.append(drink.long())

    return jsonify(
            {
                'success':True,
                'drinks':drinks_long
            }
        )

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    return get_drinks_detail_helper()


#POST /drinks
def post_drinks_helper(myrequest):
    body = myrequest.get_json()
    if body is None:
        abort(404)
    title = body.get("title", None)
    recipe = body.get("recipe", None)

    try:
        drinkobj = Drink(title=title,recipe=json.dumps(recipe))
        drinkobj.insert()
    except:
        abort(422)

    return jsonify(
            {
                'success':True,
                'drinks':drinkobj.long()
            }
        )

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    return post_drinks_helper(request)


#PATCH /drinks/<id>
def update_drinks_helper(id, myrequest):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
 
    body = myrequest.get_json()
    if body is None:
        abort(404)
    title = body.get("title", None)
    recipe = body.get("recipe", None)

    if title is not None:
        drink.title = title
    
    if recipe is not None:
        drink.recipe = json.dumps(recipe)
    drink.update()

    return jsonify(
            {
                'success':True,
                'drinks':[drink.long()]
            }
        )

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload,id):
    return update_drinks_helper(id, request)


#DELETE /drinks/<id>
def delete_drinks_helper(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()
    except:
        abort(422)

    return jsonify(
            {
                'success':True,
                'delete':id
            }
        )

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload,id):
    return delete_drinks_helper(id)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def autherror(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "Authorization failed"
    }), error.status_code
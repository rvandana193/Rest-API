'''import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from db import stores


blp = Blueprint("Stores", __name__, description:"Operation on stores")

@blp.route("/store/<string:store_id")
class Store(MethodView):
    def get(self):
        return{"stores": list(stores.values())}
        
    def post(self):
        store_data= request.get_json()
        if "name" not in store_data:
            abort(
                400,
                message = "Bad request. Ensure 'price' ,'store_id', and 'name' are included in the JSON payload"
            )
        for store in stores.values():
            if store_data["name"]== store["name"]:
                abort(400,message=f"Store already exists.")
        store_id = uuid.uuid4().hex
        store = {**store_data, "id" :store_id}
        stores[store_id] = store
        
        return store

    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message = "Store not found")


    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted"}
        except KeyError:
            abort(404, message = "Store not found")

'''
import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import StoreModel
from schemas import StoreSchema

blp = Blueprint("Stores", __name__, description="Operation on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message":"Store deleted."}

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200,StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message= "A store with that name already exists."
            )
        except SQLAlchemyError:
            abort(500, message="An error occured creating the store.")

        return store

    
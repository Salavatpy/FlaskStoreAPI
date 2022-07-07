from flask_restful import Resource, reqparse
from models.Item import ItemModel
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity


class Items(Resource):
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = ItemModel.query.all()
        if user_id:
            return {'items': [item.json() for item in items]}, 200
        return {'items': [item.name for item in items], 'message': 'To more data please log in'}, 200


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True)
    parser.add_argument('store_id', type=float, required=True)

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        else:
            return {"message": "no such item"}, 404

    @jwt_required(fresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": f"The item {name} already excist"}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occures while inserting item'}
        return item.json(), 201

    @jwt_required()
    def delete(self, name):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'You need to be an admin'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item has been deleted'}
        else:
            return {'message': 'Items does not exist'}

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, **data)
            return {'message': 'item has been created', 'item': item}, 201
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()
        return {'message': 'item has been updated'}, item.json(), 201

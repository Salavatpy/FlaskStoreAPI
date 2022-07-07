from flask_restful import Resource
from models.store import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {'message': 'Store not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'message': f'Store {name} already exist'}, 400
        else:
            store = StoreModel(name)
            try:
                store.save_to_db()
            except:
                return {'message': 'An errorr occered while inserting'}, 500
        return {'message': 'The new store created'}, store.json(), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': 'This store has been deleted'}
        else:
            return {'message': 'This store does not exist'}


class Stores(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.query.all()]}

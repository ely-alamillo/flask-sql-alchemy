import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help="Price cannot be blank."
    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": "item not found"}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            # 400 bad request
            return (
                {
                    "message": "An item with name '{}' already exists".format(
                        name
                    )
                },
                400,
            )

        data = Item.parser.parse_args()
        item = ItemModel(name, data["price"])

        try:
            item.insert()
        except:
            # 500 internal server error, not your fault ours
            return {"message": "an error occured inserting the item"}, 500

        # 201 is for created
        return item.json(), 201

    def delete(self, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {"message": "item deleted"}, 200

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
        updated_item = ItemModel(name, data["price"])

        if item is None:
            try:
                updated_item.insert()
            except:
                return {"message": "an errro occured creating the item"}, 500
        else:
            try:
                updated_item.update()
            except:
                return {"message": "an error occured updating the item"}, 500
        return updated_item.json()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "SELECT * from items"
        result = cursor.execute(query)
        items = list()
        for row in result:
            items.append({"name": row[0], "price": row[1]})

        connection.commit()
        connection.close()

        return {"items": items}

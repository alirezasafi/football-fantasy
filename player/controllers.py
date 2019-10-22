from . import (
    models
)
from flask import send_file, current_app, make_response, jsonify
from flask_restplus import Resource
from config import db


class MediaPlayer(Resource):
    def get(self, path):
        if path.endswith('.jpg'):
            img_path = current_app.config['MEDIA_ROOT'] + "/player/" + path
            try:
                return send_file(img_path, mimetype='image/jpg')
            except FileNotFoundError:
                response = make_response(jsonify({"detail": "404 NOT FOUND"}), 404)
                return response
        response = make_response(jsonify({"detail": "400 BAD REQUEST"}), 400)
        return response


def add_samples():
    players = [
        {
            'name': "Bernd Leno",
            "price": 5.0,
            "image": "Bernd Leno.jpg",
            "shirt_number": 1,
            "club": "arsenal",
            "position": "GP",
            "status": "cured"
        },
        {
            'name': "Emiliano Martínez",
            "price": 4.4,
            "image": "Emiliano Martínez.jpg",
            "shirt_number": 26,
            "club": "arsenal",
            "position": "GP",
            "status": "cured",
        },
        {
            'name': "David Luiz Moreira Marinho",
            "price": 5.8,
            "image": "David Luiz Moreira Marinho.jpg",
            "shirt_number": 23,
            "club": "arsenal",
            "position": "DF",
            "status": "cured",
        },
        {
            'name': "Sokratis Papastathopoulos",
            "price": 5.0,
            "image": "Sokratis Papastathopoulos.jpg",
            "shirt_number": 5,
            "club": "arsenal",
            "position": "DF",
            "status": "cured",
        },
        {
            'name': "Rob Holding",
            "price": 4.5,
            "image": "Rob Holding.jpg",
            "shirt_number": 16,
            "club": "arsenal",
            "position": "DF",
            "status": "cured",
        },
        {
            'name': "Shkodran Mustafi",
            "price": 5.3,
            "image": "Shkodran Mustafi.jpg",
            "shirt_number": 20,
            "club": "arsenal",
            "position": "DF",
            "status": "cured",
        },
        {
            'name': "Héctor Bellerín",
            "price": 5.4,
            "image": "Héctor Bellerín.jpg",
            "shirt_number": 2,
            "club": "arsenal",
            "position": "DF",
            "status": "cured",
        },
        {
            'name': "Daniel Ceballos Fernández",
            "price": 5.5,
            "image": "Daniel Ceballos Fernández.jpg",
            "shirt_number": 8,
            "club": "arsenal",
            "position": "MF",
            "status": "cured",
        },
        {
            'name': "Mesut Özil",
            "price": 7.2,
            "image": "Mesut Özil.jpg",
            "shirt_number": 10,
            "club": "arsenal",
            "position": "MF",
            "status": "cured",
        },
        {
            'name': "Mohamed Elneny",
            "price": 4.3,
            "image": "Mohamed Elneny.jpg",
            "shirt_number": 12,
            "club": "arsenal",
            "position": "MF",
            "status": "cured",
        },
        {
            'name': "Lucas Torreira",
            "price": 4.8,
            "image": "Lucas Torreira.jpg",
            "shirt_number": 11,
            "club": "arsenal",
            "position": "MF",
            "status": "cured",
        },
        {
            'name': "Granit Xhaka",
            "price": 5.3,
            "image": "Granit Xhaka.jpg",
            "shirt_number": 34,
            "club": "arsenal",
            "position": "MF",
            "status": "cured",
        },
        {
            'name': "Pierre-Emerick Aubameyang",
            "price": 11.1,
            "image": "Pierre-Emerick Aubameyang.jpg",
            "shirt_number": 14,
            "club": "arsenal",
            "position": "FD",
            "status": "cured",
        },
        {
            'name': "Alexandre Lacazette",
            "price": 9.3,
            "image": "Alexandre Lacazette.jpg",
            "shirt_number": 9,
            "club": "arsenal",
            "position": "FD",
            "status": "cured",
        },
        {
            'name': "Gabriel Teodoro Martinelli Silva",
            "price": 4.5,
            "image": "Gabriel Teodoro Martinelli Silva.jpg",
            "shirt_number": 90,
            "club": "arsenal",
            "position": "FD",
            "status": "cured",
        },
    ]
    for player in players:
         player_object = models.Player(
            name=player['name'],
            price=player['price'],
            image=player['image'],
            shirt_number=player['shirt_number'],
            club=player['club'],
            position=player['position'],
            status=player['status']
         )
         db.session.add(player_object)
    db.session.commit()
    print("players added")
import datetime
from typing import List, Tuple

import wtforms.validators
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from data.calculate_elos import CalculateElos
from models import Game, Base, Player

from wtforms.fields import *

import os

SECRET_KEY = os.urandom(32)

engine = create_engine("sqlite:///fsweb.sqlite", echo=True, future=True)
app = Flask(__name__)
Bootstrap5(app)
# csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = SECRET_KEY
Base.metadata.create_all(engine)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/nav', methods=['GET', 'POST'])
def test_nav():
    return render_template('nav.html')


@app.route("/games", methods=['GET'])
def games():
    with Session(engine) as session:
        query = session.query(Game)
        all_games = [g for g in query]

        return render_template("games.html", games=all_games)


@app.route("/players", methods=['GET'])
def players():
    with Session(engine) as session:
        all_players = session.scalars(select(Player))
        elos = CalculateElos(engine).get_elos()
        return render_template("players.html", players=all_players, elos=elos)


def all_players():
    with Session(engine) as session:
        query = session.query(Player)
        all_players_names = [p.name for p in query]
    return all_players_names


class AddGameForm(FlaskForm):
    b1 = SelectField(label='Blue Defence', choices=all_players())
    b2 = SelectField(label='Blue Attack', choices=all_players())
    blue_points = IntegerField(label='Red goals')
    red_points = IntegerField(label='Blue goals')
    r1 = SelectField(label='Red Defence', choices=all_players())
    r2 = SelectField(label='Red Attack', choices=all_players())
    submit = SubmitField()


@app.route("/addgame", methods=['GET', 'POST'])
def addgame():
    with Session(engine) as session:
        query = session.query(Game)
        all_games = [g for g in query]

        if request.method == 'POST':
            values = request.values

            all_players = [values['r1'], values['r2'], values['b1'], values['b2']]
            # Validate game makes sense
            if len(all_players) > len(set(all_players)):
                print("not unique")
            else:
                game = Game(date=datetime.datetime.datetime.today(),
                            blue_p1_id=values['b1'],
                            blue_p2_id=values['b2'],
                            blue_points=values['blue_points'],
                            red_p1_id=values['r1'],
                            red_p2_id=values['r2'],
                            red_points=values['red_points'],
                            )
                print(game)
        return render_template("addgame.html", form=AddGameForm(), games=all_games)


@app.route("/addplayer")
def addplayer():
    with Session(engine) as session:
        all_players = session.scalars(select(Player))
        elos = CalculateElos(engine).get_elos()
        return render_template("players.html", players=all_players, elos=elos)


if __name__ == '__main__':
    app.run(port=3000)

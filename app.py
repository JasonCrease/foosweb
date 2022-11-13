import datetime
import os

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from wtforms.fields import *

import models
from data.calculate_elos import CalculateElos
from models import Game, Base, Player

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
        query = session.query(Game).order_by(models.Game.date.desc())
        all_games = [g for g in query]

        return render_template("games.html", games=all_games)


@app.route("/players", methods=['GET'])
def players():
    with Session(engine) as session:
        all_players = session.scalars(select(Player))
        elos = CalculateElos(engine).get_elos()
        return render_template("players.html", players=all_players, elos=elos)


def all_player_names():
    with Session(engine) as session:
        query = session.query(Player)
        all_players_names = [p.name for p in query]
    return all_players_names


def all_player_id_names():
    with Session(engine) as session:
        query = session.query(Player)
        id_names = [(p.id, p.name) for p in query.order_by(Player.name)]
    return id_names


class AddGameForm(FlaskForm):
    b1 = SelectField(label='Blue Defence', choices=[])
    b2 = SelectField(label='Blue Attack', choices=[])
    blue_points = IntegerField(label='Blue goals')
    red_points = IntegerField(label='Red goals')
    r1 = SelectField(label='Red Defence', choices=[])
    r2 = SelectField(label='Red Attack', choices=[])
    submit = SubmitField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Update choices
        self.b1.choices = all_player_id_names()
        self.b2.choices = all_player_id_names()
        self.r1.choices = all_player_id_names()
        self.r2.choices = all_player_id_names()


@app.route("/addgame", methods=['GET', 'POST'])
def addgame():
    if request.method == 'POST':
        values = request.values

        # Validate game makes sense
        game_players = [values['b1'], values['b2'], values['r1'], values['r2']]
        if len(game_players) > len(set(game_players)):
            return render_template("addgame.html", form=AddGameForm(), error_message="Duplicate players.")
        # isdigit guarantees it's a non-negative integer
        if not str.isdigit(values['blue_points']) or not str.isdigit(values['red_points']):
            return render_template("addgame.html", form=AddGameForm(), error_message="Goals must be "
                                                                                     "non-negative integers.")

        game = Game(date=datetime.datetime.datetime.today(),
                    blue_p1_id=values['b1'], blue_p2_id=values['b2'], blue_points=values['blue_points'],
                    red_p1_id=values['r1'], red_p2_id=values['r2'], red_points=values['red_points'])
        with Session(engine) as session:
            session.add(game)
            session.commit()
            session.flush()
        return render_template("addgame.html", form=AddPlayerForm(), success_message="")
    return render_template("addgame.html", form=AddGameForm())


class AddPlayerForm(FlaskForm):
    player_name = StringField(label='Player name')
    submit = SubmitField()


@app.route("/addplayer", methods=['GET', 'POST'])
def addplayer():
    if request.method == 'POST':
        player_name = request.values['player_name'].strip()

        with Session(engine) as session:
            query = session.query(Player)

            # Validate player name is not yet taken
            if player_name is None or str(player_name) == "":
                return render_template("addplayer.html", form=AddPlayerForm(),
                                       error_message="Name cannot be empty.")
            if player_name in [p.name for p in query]:
                return render_template("addplayer.html", form=AddPlayerForm(),
                                       error_message=f"Name '{player_name}' already taken.")
            player = Player(name=player_name)
            session.add(player)
            session.commit()
            session.flush()
            return render_template("addplayer.html", form=AddPlayerForm(),
                                   success_message=f"Player {player_name} added")
    return render_template("addplayer.html", form=AddPlayerForm())


if __name__ == '__main__':
    app.run(port=3000)

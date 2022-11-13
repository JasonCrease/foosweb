import datetime
import random

import numpy
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Game, Base, Player

engine = create_engine("sqlite:///./../fsweb.sqlite", echo=True, future=True)


def insert_players(csv_df: pd.DataFrame):
    all_name_values = np.concatenate((csv_df['r1'].values, csv_df['r2'].values,
                                      csv_df['b1'].values, csv_df['b2'].values))
    # Uniquify, trim whitespace, and put in numpy array
    unique_names = np.array([name.strip() for name in numpy.unique(all_name_values)])

    with Session(engine) as session:
        for player_name in unique_names:
            session.add_all([Player(name=player_name)])
        session.commit()


def insert_games(csv_df: pd.DataFrame):
    with Session(engine) as session:
        # build name -> id lookup table
        player_ids = {player.name: player.id for player in session.query(Player).all()}

        MAX_GAMES = 200
        games_seen = 0

        game_date = datetime.datetime.today()

        for raw_row in csv_df.iterrows():
            row = raw_row[1]
            game = Game(date=game_date,
                        blue_p1_id=player_ids[row['b1']],
                        blue_p2_id=player_ids[row['b2']],
                        blue_points=row['blue_goals'],
                        red_p1_id=player_ids[row['r1']],
                        red_p2_id=player_ids[row['r2']],
                        red_points=row['red_goals']
                        )
            games_seen = games_seen + 1
            session.add_all([game])
            if games_seen > MAX_GAMES:
                break
            if random.random() > 0.7:
                game_date = game_date - datetime.timedelta(days=1)

        session.commit()
        session.flush()


def main():
    # Delete all data
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with open('../resources/results1.csv', 'r') as f:
        csv_df = pd.read_csv(f, lineterminator='\n')
        insert_players(csv_df)
        insert_games(csv_df)


if __name__ == '__main__':
    main()

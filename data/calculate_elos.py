import pandas as pd
from pandas import DataFrame
from sklearn.linear_model import LogisticRegression
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from models import Game


class CalculateElos:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_elos(self):
        train_data = self.convert_to_goals_list()

        player_names = list(train_data.iloc[:, 1:].columns)
        x_train = train_data[player_names]
        y_train = train_data['result'].astype('int')

        lr_model = LogisticRegression()
        lr_model.fit(x_train, y_train)
        # For debugging. Should be close to zero
        # print(lr_model.intercept_)

        return_table = {}

        for player_id, ability in sorted(list(zip(player_names, lr_model.coef_[0])), key=lambda x: x[1], reverse=True):
            return_table[player_id] = (ability * 400 + 1000)

        return return_table

    def convert_to_goals_list(self) -> DataFrame:

        with Session(self.engine) as session:
            query = session.query(Game)
            goal_rows = []

            for row in query:
                # Each row, result is 1 if the goal was by red against blue, and 0 if blue against red.
                # 1 means a red player, -1 means blue. 0 means not involved. One row for each goal.
                red_goal = {'result': 1,
                            row.red_p1_id: 1,
                            row.red_p2_id: 1,
                            row.blue_p1_id: -1,
                            row.blue_p2_id: -1}
                for i in range(row.red_points):
                    goal_rows.append(red_goal)

                blue_goal = {'result': 0,
                             row.red_p1_id: 1,
                             row.red_p2_id: 1,
                             row.blue_p1_id: -1,
                             row.blue_p2_id: -1}
                for i in range(row.blue_points):
                    goal_rows.append(blue_goal)

            goals_df = pd.DataFrame(data=goal_rows)
            goals_df = goals_df.fillna(int(0))
            # Change floats to ints
            goals_df = goals_df.convert_dtypes()
            return goals_df


if __name__ == '__main__':
    fweb_engine = create_engine("sqlite:///./../fsweb.sqlite", echo=True, future=True)
    elos = CalculateElos(fweb_engine).get_elos()
    print(elos)

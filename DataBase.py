import sqlite3

# xbox_games: game_id, genre, release_date, opt_series, localization


def connect():
    con = sqlite3.connect('db.sql')
    cur = con.cursor()
    return con, cur


def check_id(game_id):
    con, cur = connect()
    data = cur.execute(f"SELECT game_id FROM xbox_games WHERE game_id='{game_id}'").fetchone()
    close(con)
    return data


def get_genre(game_id):
    con, cur = connect()
    data = cur.execute(f"SELECT genre FROM xbox_games WHERE game_id='{game_id}'").fetchone()
    close(con)
    return data


def get_release_date(game_id):
    con, cur = connect()
    data = cur.execute(f"SELECT release_date FROM xbox_games WHERE game_id='{game_id}'").fetchone()
    close(con)
    return data


def get_opt_series(game_id):
    con, cur = connect()
    data = cur.execute(f"SELECT opt_series FROM xbox_games WHERE game_id='{game_id}'").fetchone()
    close(con)
    return data


def insert_id(game_id, genre, rel_date, opt_ser):
    con, cur = connect()
    cur.execute(f"INSERT INTO xbox_games VALUES ('{game_id}', '{genre}', '{rel_date}', '{opt_ser}')")
    close(con)


def get_ids():
    con, cur = connect()
    data = cur.execute(f"SELECT game_id FROM xbox_games").fetchall()
    close(con)
    return data


def close(con):
    con.commit()
    con.close()

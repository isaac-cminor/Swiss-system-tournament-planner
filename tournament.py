#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a connection and cursor."""
    try:
        db = psycopg2.connect("dbname ={}".format (database_name))
        cursor = db.cursor()
        return db , cursor
    except:
        print "Error while trying to connect to database"
 


def deleteMatches():
    """Remove all the match records from the database."""
    db,cursor = connect()
    cursor.execute("""TRUNCATE matches;""")
    db.commit()
    db.close()



def deletePlayers():
    """Remove all the player records from the database."""
    db,cursor = connect()
    cursor.execute("""TRUNCATE players from CASCADE;""")
    db.commit()
    db.close()


def countPlayers(tournament_id = 0):
    """Returns the number of players currently registered.
       If no arguments are given, then function returns the
       count of all registered players.

       Args:
        tournament_id: the id (integer) of the tournament.

       Returns:
        An integer of the number of registered players if tournament_id
        is not specified. If tournament_id is specified, returns an
        integer of the number of players in given tournament (who have
        played at least 1 game).
        
    """
    db, cursor = connect()

    if tournament_id == 0:
        cursor.execute("""SELECT COUNT(id) FROM players;""")
    else:
        cursor.execute("""SELECT CAST(COUNT(subQuery.X) AS INTEGER) FROM
                    (SELECT winner_id AS X
                     FROM matches WHERE matches.tournament_id = %s
                     UNION
                     SELECT loser_id AS X
                     FROM matches WHERE matches.tournament_id = %s)
                     AS subQuery;""", (tournament_id, tournament_id))

    output_ = cursor.fetchone()[0]
    db.close()
    return output_



def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor = connect()

    # add player to players table and return its id:
    query = "INSERT INTO players(name) VALUES(%s) RETURNING id;"
    param = (name,)
    cursor.execute(query, param)
    return_id = cursor.fetchone()[0]

    db.commit()
    db.close()
    return return_id


def playerStandings(tournament_id=0):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = connect()

    # check how many matches have been played:
    query = """SELECT COUNT(match_id) FROM matches 
               WHERE matches.tournament_id = %s;"""
    param = (tournament_id,)
    cursor.execute(query, param)
    total_matches = cursor.fetchone()[0]

    # if no matches have been played, return registered players:
    if total_matches == 0:
        cursor.execute("""SELECT id, name, 0, 0 FROM players;""")
        output_ = cursor.fetchall()
        db.close()
        return output_

    if tournament_id != 0:
        tournament_restriction = 'AND games_played > 0'
    else:
        tournament_restriction = ''
    # (subquery combines wins-count data with opponent wins (omw) &
    # select number of games played)
    cursor.execute("""SELECT subQuery.id, subQuery.name, wins,
             CAST(games_played AS INTEGER)
             FROM num_matches,
                  (SELECT games_won.id AS id, name,
                   CAST(wins AS INTEGER),
                   COALESCE(opponent_wins, 0) AS opponent_wins
                   FROM games_won LEFT JOIN omw
                   ON id = x)
                   AS subQuery
             WHERE (subQuery.id = num_matches.id) %s
             ORDER BY wins DESC, opponent_wins DESC,
             games_played ASC;""" % tournament_restriction)

    output_ = cursor.fetchall()
    db.close()
    return output_


def reportMatch(winner, loser,tournament_id=0):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db, cursor = connect()

    # Add players into matches table:
    query = "INSERT INTO matches (winner_id, loser_id, tournament_id) \
            VALUES(%s, %s, %s);"
    param = (winner, loser, tournament_id)
    cursor.execute(query, param)

    db.commit()
    db.close()

 
def swissPairings(tournament_id=0):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = player_standings(tournament_id)

    pairings = []
    iii = 1
    while iii < len(standings):
        tup1 = standings[iii-1]
        tup2 = standings[iii]

        pairings.append(tuple((tup1[0], tup1[1], tup2[0], tup2[1])))
        iii += 2

    return pairings


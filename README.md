# Swiss-system-tournament-planner
This planner is a game tournament that uses the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

## Installation
 * If you don't already have Vagrant VM, you can [download it here](https://www.virtualbox.org/wiki/Downloads) and install it on your machine.
 * Download the [latest release of Swiss-system Tournament Planner](https://github.com/Ogodei/Swiss-Tournament-Planner/archive/master.zip) from GitHub.
 * Extract the zipped files to your Vagrant directory.
 * From the terminal, cd to your `/vagrant` directory.
 * Type `vagrant up` to launch the virtual machine. Then type `vagrant ssh` to log in.
 * In the VM, `cd` to the `/tournament` folder.
 * Setup the PostgreSQL database with the command, `psql -f tournament.sql`
 
 ## Usage
Add players into database with the `register_player()` function which takes a single string argument.

``` register_player("TeamName") ```

Almost all of the other functions have the optional `tournament_id` argument, which specifies the tournament of which the match belonged. This allows the Swiss-system Tournament Planner to track, archive, and calculate the rankings and matchups of multiple tournaments concurrently. We can also have the same individual participate in multiple tournaments simultaneously.

Report and archive match results with the `report_match()` function. Insert the id's of the winner and loser of a match, respectively (with the optional tournament_id argument).

``` report_match(12,17) ```

Simply call the `swiss_pairings()` function, and the module will calculate the next pair of player matchups for a given tournament. Finally, player_standings() returns the current rankings/standings of the given tournament.

## What's included
Inside the **Swiss-system Tournament Planner** directory, you'll find the following files:


``` 
Swiss Tournament Planner/
    ├──tournament.py
    ├──tournament.sql
    ├──tournament_test.sql
    └──README.md 
```
    
## License
MIT License.

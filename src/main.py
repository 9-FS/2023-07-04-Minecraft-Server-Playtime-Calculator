# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import datetime as dt
import json
from KFSconfig import KFSconfig
from KFSfstr   import KFSfstr
from KFSlog    import KFSlog
from KFSsleep  import KFSsleep
import logging
import os
import re
from exec_server_command import exec_minecraft_server_command
from Log                 import Log
from Player              import Player


@KFSlog.timeit
def main() -> None:
    
    log: Log                                    # 1 log file
    player_joined_dt: dt.datetime               # when did player join
    PLAYER_JOINED_PATTERN=r"^(\[(?P<time_hour>[0-2][0-9]):(?P<time_minute>[0-5][0-9]):(?P<time_second>[0-5][0-9])] \[.*?]: (?P<player_name>[0-9a-zA-Z_]+) joined the game)$"
    player_left_dt: dt.datetime                 # when did player leave
    PLAYER_LEFT_PATTERN=r"^(\[(?P<time_hour>[0-2][0-9]):(?P<time_minute>[0-5][0-9]):(?P<time_second>[0-5][0-9])] \[.*?]: (?P<player_name>[0-9a-zA-Z_]+) left the game)$"
    players: list[Player]                       # list of all players and their playtime
    settings: dict[str, str]                    # minecraft_server_screen_name, log_path
    settings_default: dict[str, str]={          # linux screen name to attach to for server commands
        "minecraft_server_screen_name": "",
        "log_path": "",
    }

    try:
        settings=json.loads(KFSconfig.load_config("./config/settings.json", json.dumps(settings_default, indent=4)))
    except FileNotFoundError:
        return
    

    while True:
        players=[]  # reset player data

        logging.info("--------------------------------------------------")
        logging.info(f"Loading log filenames from \"{settings['log_path']}\"...")
        log_filenames=sorted([filename for filename in os.listdir(settings["log_path"]) if os.path.isfile(os.path.join(settings["log_path"], filename))==True])
        logging.info(f"\rLoaded log filenames from \"{settings['log_path']}\".")
        logging.debug(log_filenames)

        for log_filename in log_filenames:              # go through all log filenames
            match os.path.splitext(log_filename)[1]:    # create Log object from filename, construction depends on file extension (zipped or not zipped)
                case ".gz":
                    log=Log(os.path.join(settings["log_path"], log_filename))
                case ".log":
                    log=Log(os.path.join(settings["log_path"], log_filename), dt.date.today())
                case _:
                    logging.warning(f"Log file \"{log_filename}\" has neither \".gz\" nor \".log\" as file extension. Skipping...")
                    continue
            
            
            log_lines=log.content.split("\n")                                                               # split log content into single lines
            for log_line_i, log_line in enumerate(log_lines):                                               # go through each line of the log content
                logging.debug(f"Going through \"{log.filename}\", line {log_line_i+1}/{len(log_lines)}...")
                re_match=re.search(PLAYER_JOINED_PATTERN, log_line)                                         # see if log line matches player joined
                if re_match!=None:
                    if re_match.groupdict()["player_name"] not in [player.name for player in players]:      # if player does not exist yet in player list: create player
                        players.append(Player(re_match.groupdict()["player_name"]))
                    
                    player_i=[player.name for player in players].index(re_match.groupdict()["player_name"]) # relevant player index
                    player_joined_dt=dt.datetime.combine(log.date, dt.time(int(re_match.groupdict()["time_hour"]), int(re_match.groupdict()["time_minute"]), int(re_match.groupdict()["time_second"])), dt.timezone.utc)
                    players[player_i].last_join=player_joined_dt                                            # enter last joined datetime
                    logging.debug(f"At {player_joined_dt.strftime('%Y-%m-%dT%H:%M:%S')} player \"{players[player_i].name}\" joined the game.")
                    players[player_i].is_online=True                                                        # joined the game, so is online

                re_match=re.search(PLAYER_LEFT_PATTERN, log_line)                                           # see if log line matches player left
                if re_match!=None:
                    if re_match.groupdict()["player_name"] not in [player.name for player in players]:      # if player does not exist yet in player list: create player
                        players.append(Player(re_match.groupdict()["player_name"]))
                    
                    player_i=[player.name for player in players].index(re_match.groupdict()["player_name"]) # relevant player index
                    player_left_dt=dt.datetime.combine(log.date, dt.time(int(re_match.groupdict()["time_hour"]), int(re_match.groupdict()["time_minute"]), int(re_match.groupdict()["time_second"])), dt.timezone.utc)
                    if players[player_i].last_join==None:                                                   # leaving but no prior join defined: something is not right
                        logging.warning(f"At {player_left_dt.strftime('%Y-%m-%dT%H:%M:%S')} player \"{players[player_i].name}\" left the game without joining it before.")
                        continue
                    players[player_i].playtime+=(player_left_dt-players[player_i].last_join) # type:ignore
                    logging.debug(f"At {player_left_dt.strftime('%Y-%m-%dT%H:%M:%S')} player \"{players[player_i].name}\" left the game after playing for {KFSfstr.notation_tech((player_left_dt-players[player_i].last_join).total_seconds(), 2)}s. Total playtime: {KFSfstr.notation_tech(players[player_i].playtime.total_seconds(), 2)}s") # type:ignore
                    players[player_i].last_join=None
                    players[player_i].is_online=False   # player left the game, so is offline


        players=sorted(players, key=lambda player: player.playtime.total_seconds(), reverse=True)   # sort players by playtime
        logging.info("Playtimes:")
        logging.info("\n".join([f"{player.name}: {KFSfstr.notation_tech(player.playtime.total_seconds(), 0, round_static=True)}s" for player in players]))

        for player in players:
            if player.is_online==True:                                                                                                                                          # if player currently online:
                player.playtime+=(dt.datetime.now(dt.timezone.utc)-player.last_join)                                                                                            # add playtime from last join until now # type:ignore
            exec_minecraft_server_command(f"scoreboard players set {player.name} playtime {round(player.playtime.total_seconds())}", settings["minecraft_server_screen_name"])  # update scores ingame

        KFSsleep.sleep_mod(5000)
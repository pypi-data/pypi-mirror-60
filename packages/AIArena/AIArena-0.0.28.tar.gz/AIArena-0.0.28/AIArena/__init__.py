import AIArena.games
from AIArena.AI import AI as AI


from AIArena.Human import Human_Connect4 as Human_Connect4
from AIArena.upload import upload

import pkgutil
import requests
import os
from brainiac_client.scientist import package


import json

name = "AIArena"

def runGame(Ais,game):
    gameName = game["name"]
    result = {
        "error":"None",
        "version":28
    }
    #Game setup
    try:
        if gameName == "Connect4":
            game = AIArena.games.Connect4(players=Ais)
        else:
            result["error"] = "Game Creation: Bad Name"
            return result
    except:
        result["error"] = "Game Creation"
        return result

    #Game run
    """try:
        gameResult = game.runGame(False)
        result.update(gameResult)
    except:
        result["error"] = "Game Run"
        result["replayState"] = game.replayStates
        return result"""
    gameResult = game.runGame(False)
    result["replayState"] = game.replayStates
    result.update(gameResult)

    return result

def runMove(AIs, data):
    try:
        AI = AIs[0]
        state = json.loads(data["gamestate"])
        move = AI.makeMove(state)

        results = {
            "error": "None"
        }

        if move == None:
            results['error'] = 'Bad move response'
        else:
            results['move'] = move

        return results
    except Exception as e:
        print("EXCEPTION:", e)
        return {'exception': e}



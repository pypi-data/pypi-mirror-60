import asyncio
import random
import time
import uuid
import pickledb

from flask import Flask, abort, g, jsonify, request, session, Response

from .DynamicEventLoop import DynamicEventLoop
from .Pointa import Player, Pointa

data = None

app = Flask(__name__)

class Data:
    def __init__(self):
        self.playerList = {}
        self.matchList = {}
        self.req = 0
        self.taskList = {}
        self.matchMakers = []
        self.db = pickledb.load('record.db', False, sig=False)

data = Data()
Del = DynamicEventLoop()
Del.run()

# Lag Remover
@app.before_request
def before():
    global data
    global Del
    data.req += 1
    if data.req % 1000 == 0:
        temps = [
            list(data.playerList.items()),
            list(Del.taskList.items())
        ]
        for key, p in temps[0]:  # Overtime Detection
            if int(time.time()) - p[1] >= 120:
                data.playerList.pop(key)
        for key, ga in temps[1]:  # Done match Detection
            if ga.done():
                Del.pop(key)

# Handling Requests Outside the Game period
@app.route('/outGame/<key>', methods=['POST'])
def outGameHandler(key):
    global data
    global Del
    req = request.get_json(force=True)

    if req['Action'] == 'Ready':
        # Generate a uid as key
        uid = uuid.uuid5(uuid.NAMESPACE_DNS, request.remote_addr + str(random.randint(0, 100)))
        data.playerList.update({str(uid): [
            Player(str(uid)),
            int(time.time()),  # Last Communicate time
            req['Target'] # Player's Username
        ]})
        return jsonify({
            'UUID': str(uid),
            'Online': len(data.playerList)
        })

    elif req['Action'] == 'Invite':

        data.playerList[key][1] = int(time.time())

        if req['Target'] in data.playerList.keys():

            # Create match
            match = Pointa(
                    data.playerList[key][0],
                    data.playerList[req['Target']][0],
                    Del.loop
                )
            Del.append(match, match.main())

            # Add to matchlist
            keys = (key + ',' + req['Target'])
            data.matchList.update({
                keys: match
            })

            # Record happend match
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data.db.set(now, keys)
            data.db.dump()

            return jsonify({'targetName': data.playerList[req['Target']][2]})
        else:
            abort(404)

    elif req['Action'] == 'Quit':
        try:
            data.playerList.pop(key)
        except KeyError:
            pass
        return Response('ok.')

    elif req['Action'] == 'Matchmaking':
        if len(data.matchMakers) == 0:
            data.matchMakers.append(key)
        else:
            another = data.matchMakers.pop(0)
            match = Pointa(
                data.playerList[key][0],
                data.playerList[another][0],
                Del.loop
            )
            Del.append(match, match.main())
            keys = (key + ',' + another)
            data.matchList.update({
                keys: match
            })
        return Response('ok.')

# Handling Requests in the Game period
@app.route('/inGame/<key>', methods=['GET', 'POST'])
def inGameHandler(key):
    global data
    global Del
    Data = data

    # Updating last communicating time
    try:
        data.playerList[key][1] = int(time.time())
    except KeyError:
        abort(404)  # Player not found

    currentMatches = []

    # Find current match
    for match in data.matchList.items():
            if key in match[0].split(','):
                currentMatches.append(match[1])
                another = [x for x in match[0].split(',') if x!=key][0]
                break

    try:
        currentMatch = currentMatches[0]
    except IndexError:
        abort(404)  # Match not found

    # Insert Action
    if request.method == 'POST':
        req = request.get_json(force=True)
        if currentMatch.round['phase'] == 2:
            dat = req['Action']
            res = Data.playerList[key][0].action({
                0: int(dat[0]),
                1: int(dat[1]),
                2: int(dat[2])
            })
            if res:
                return jsonify({'Action': 'Accepted'})
        abort(405)

    elif request.method == 'GET':
        # Get request args
        fTS = int(request.args.get("fts"))
        roundL = int(request.args.get("r"))
        phaseL = int(request.args.get("p"))
        # Sync Local Vars to Player Object
        Data.playerList[key][0].localVar = {
            'round': roundL,
            'phase': phaseL
        }

        # Get Updated Log
        stat = currentMatch.getStat()
        uptLog = list(
            filter(
                lambda x: x['time'] > fTS,
                stat['log']
            )
        )

        anotherAction = {}
        selfAction = {}
        # Avoid Client Cheating
        if currentMatch.round['phase'] == 3:
            anotherAction = stat['players'][another].actions
            selfAction = stat['players'][key].actions

        try:
            username = Data.playerList[stat['players'][another].key][2]
        except KeyError:
            abort(404)

        # Return Sync Result in Standard Format
        return jsonify(
            {
                'UpdatedLog': uptLog,
                'playerStats': {
                    'self': [
                        stat['players'][key].properties,
                        selfAction
                    ],
                    'another': [
                        stat['players'][another].properties,
                        anotherAction,
                        stat['players'][another].key,
                        Data.playerList[stat['players'][another].key][2]  # Username
                    ]
                }
            }
        )

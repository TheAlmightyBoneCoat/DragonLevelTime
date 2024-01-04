import json
import getopt
import pdb

USING_FNAME = "./data/using.json"
DEFAULT_FNAME = "./data/defaults.json"

# Turns list of strings into one big string
def linesToString(lines):
    result = ""
    for i in range(len(lines)):
        result += lines[i]
    return result

# Gets dragon level args
def getLevels(args):
    arg1 = 0
    arg2 = 0
    # Test each arg for int-ness
    # and assign the first two ints we find
    for arg in args:
        try:
            if (arg1 == 0):
                arg1 = int(arg)
            else:
                arg2 = int(arg)
                break
        except ValueError:
            continue

    return arg1, arg2

# Gets the method data and venue data
# and returns one big ol' JSON string of both
def getVenueFileData(venueFName = "./data/venues/kelp_beds.json"):
    #pdb.set_trace()
    venueFile = open(venueFName, "r")
    venueString = linesToString(venueFile.read().splitlines())

    venueFile.close()
    return venueString

def getMethodFileData(methodFName = USING_FNAME):
    methodFile = open(methodFName, "r")
    methodString = (linesToString(methodFile.read().splitlines()))

    methodFile.close()
    return methodString

# Packages up the args in a dictionary
def getCommandData(arguments):
    opts, raw_args = getopt.getopt(arguments,
            'bs:t:u:v:x:', ['stage=', 'time_per_battle=', 'time=', 'first=', 
            'first_battle=', 'venue=', 'file_using=', 'using=', 'bosses',
            'fodder=', 'num_fodder=', 'upath=', 'using_path=', 'vpath=', 
            'venue_path=', 'spath=', 'stage_path=', 'xp_so_far='])

    result = {"currentLevel" : 0, "desiredLevel" : 0}

    # Separate the levels out from the args
    i = -1
    args = []
    if len(raw_args) > 0:
        while i + 1 < len(raw_args):
            i += 1
            # Skip non-level arguments
            if raw_args[i][0] == '-':
                i += 1
            else:
                try:
                    args.append(int(raw_args[i]))
                except ValueError:
                    continue

    # Were two levels specified?
    if (len(args) > 1):
        result["currentLevel"] = args[0]
        result["desiredLevel"] = args[1]
    else:
        # Were any levels specified?
        if (len(args) == 1):
            result["currentLevel"] = 1
            result["desiredLevel"] = args[0]

    for option in opts:
        # Strip opening hyphens
        if option[0][1] == "-":
            result[option[0][2:]] = option[1]
        else:
            result[option[0][1:]] = option[1]

    return result

# Returns relevant vars based on command args and file data
def getData(args):
    commandData = getCommandData(args)
    methodFileString = ""

    # Does commandData define method file's data for us?
    methodFileData = ""
    if (("time" in commandData or "time_per_battle" in commandData or
            "t" in commandData) and ("v" in commandData or
            "venue" in commandData) and ("f" in commandData or
            "first" in commandData or "first_battle" in commandData) and
            ("fodder" in commandData or "num_fodder" in commandData)):
        pass
    else:
        # Go to the specified using file
        if "u" in commandData:
            methodFileString = getMethodFileData(
                    "./data/" + commandData["u"] + ".json")
        elif "using" in commandData:
            methodFileString = getMethodFileData(
                    "./data/" + commandData["using"] + ".json")
        elif "file_using" in commandData:
            methodFileString = getMethodFileData(
                    "./data/" + commandData["file_using"] + ".json")
        elif "upath" in commandData:
            methodFileString = getMethodFileData(commandData['upath'])
        elif "using_path" in commandData:
            methodFileString = getMethodFileData(commandData['using_path'])
        else:
            methodFileString = getMethodFileData()
        methodFileData = json.loads(methodFileString)

    # Get venue data from specified file
    venueFileString = ""
    if "v" in commandData:
        venueFileString = getVenueFileData(
                "./data/venues/" + commandData["v"] + ".json")
    elif "venue" in commandData:
        venueFileString = getVenueFileData(
                "./data/venues/" + commandData["venue"] + ".json")
    elif "s" in commandData:
        venueFileString = getVenueFileData(
                "./data/venues/" + commandData["s"] + ".json")
    elif "stage" in commandData:
        venueFileString = getVenueFileData(
                "./data/venues/" + commandData["stage"] + ".json")
    elif 'spath' in commandData:
        venueFileString = getVenueFileData(commandData['spath'])
    elif 'stage_path' in commandData:
        venueFileString = getVenueFileData(commandData['stage_path'])
    elif 'vpath' in commandData:
        venueFileString = getVenueFileData(commandData['vpath'])
    elif 'venue_path' in commandData:
        venueFileString = getVenueFileData(commandData['venue_path'])
    else:
        venueFileString = getVenueFileData(methodFileData["VENUE"])

    # Finally, let's put it all together
    venueFileData = json.loads(venueFileString)
    result = { "currentLevel" : 0 }

    result["currentLevel"] = commandData["currentLevel"]
    result["desiredLevel"] = commandData["desiredLevel"]

    # Seconds per average battle
    if "t" in commandData:
        result["secsPerBattle"] = commandData["t"]
    elif "time" in commandData:
        result["secsPerBattle"] = commandData["time"]
    elif "time_per_battle" in commandData:
        result["secsPerBattle"] = commandData["time_per_battle"]
    else:
        result["secsPerBattle"] = methodFileData["SECS_PER_BATTLE"]

    # Seconds per setup battle
    if "first" in commandData:
        result["secsFirstBattle"] = commandData["first"]
    elif "first_battle" in commandData:
        result["secsFirstBattle"] = commandData["first_battle"]
    else:
        result["secsFirstBattle"] = methodFileData["SECS_FIRST_BATTLE"]

    # Number of fodder in the venue
    if "fodder" in commandData:
        result["numFodder"] = commandData["fodder"]
    elif "num_fodder" in commandData:
        result["numFodder"] = commandData["num_fodder"]
    else:
        result["numFodder"] = methodFileData["NUM_FODDER"]

    if "x" in commandData:
        result["xpSoFar"] = commandData["x"]
    elif "xp_so_far" in commandData:
        result["xpSoFar"] = commandData["xp_so_far"]
    else:
        result["xpSoFar"] = 0

    if "b" in commandData:
        result["bosses"] = True
    elif "bosses" in commandData:
        result["bosses"] = True
    else:
        result["bosses"] = False

    result["xpPerMonster"] = venueFileData["XP_PER_MONSTER"]
    result["xpPerBoss"] = venueFileData["XP_PER_BOSS"]
    result["nonBossMonsters"] = venueFileData["NON_BOSS_MONSTERS"]
    result["bossMonsters"] = venueFileData["BOSS_MONSTERS"]
    result["monstersPerFight"] = venueFileData["MONSTERS_PER_FIGHT"]
    result["usingXPChain"] = venueFileData["XP_CHAIN"]

    return result    

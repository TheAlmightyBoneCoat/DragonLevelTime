# Credits:
# Author: TheAlmightySand
# Battle XP mechanics from: https://www1.flightrising.com/forums/gde/1046488
# Exalt payout formula from: https://www1.flightrising.com/forums/gde/746775

import json
import sys
import pdb
import math

from data.getData import getData

TOTAL_XP_PER_LEVEL = [0, 0, 245, 886, 2287, 6314, 11859, 20239, 32120, 
        48129, 69655, 97331, 131595, 170551, 216227, 270388, 331269,
        403235, 484854, 577289, 681852, 793539, 921048, 1057258,
        1204710, 1363652]

# Is the list level-indexed or level-minus-one indexed?
# Don't worry about it! Just call this
def xpFromLevel(level):
    try:
        return TOTAL_XP_PER_LEVEL[level]
    except IndexError:
        print("Valid dragon levels are between 1 and 25.")
        sys.exit(0)

# Make sure user didn't put in cumulative xp for whatever godforsaken reason
# DEPRECATED: I have no idea why this even would have been used
def getXPSoFar(xpSoFar, currentLevel):
    levelThreshold = xpFromLevel(currentLevel)
    if levelThreshold < xpSoFar:
        return xpSoFar - levelThreshold
    return xpSoFar

def levelFromXP(xp, startLevel):
    MAX_LEVEL = 25

    if (startLevel >= MAX_LEVEL):
        return MAX_LEVEL

    xpSoFar = 0
    for i in range(startLevel + 1, len(TOTAL_XP_PER_LEVEL)):
        xpSoFar += xpFromLevel(i) - xpFromLevel(i - 1)
        if xpSoFar > xp:
            return i - 1

    return MAX_LEVEL

def payoutFromLevel(level):
    return 750 + (1500 * level)

def levelFromPayout(payout):
    return (payout - 750) / 1500

def profitHour(profit, seconds):
    SECONDS_PER_HOUR = 3600
    return profit / (seconds * SECONDS_PER_HOUR)

def getTimeFromBattles(numBattles, secsPerBattle, secsFirstBattle):
    if numBattles < 1:
        return 0
    else:
        return secsFirstBattle + ((numBattles - 1) * secsPerBattle)

def getBattlesFromTime(totalSecs, secsPerBattle, secsFirstBattle):
    if totalSecs < secsFirstBattle:
        return 0
    totalSecs -= secsFirstBattle
    result = 1
    result += math.ceil(totalSecs / secsPerBattle)

    return result

def getBattlesFromXP(totalXP, xpPerBattle, usingXPChain):
    xpChain = 1.05
    result = 0

    if usingXPChain:
        # Work our way up to max XP chain
        while totalXP > 0 and xpChain < 1.16:
            result += 1
            totalXP -= xpPerBattle * xpChain
            xpChain += 0.05
    else:
        xpChain = 1

    result += math.ceil(totalXP / (xpPerBattle * xpChain))
    return result

def xpFromBattles(totalBattles, xpPerBattle, usingXPChain):
    xpChain = 1.05
    result = 0
    if usingXPChain:
        while totalBattles > 0 and xpChain < 1.16:
            totalBattles -= 1
            result += xpPerBattle * xpChain
            xpChain += 0.05
    else:
        xpChain = 1

    # Now that we have our max XP chain, calculating the rest is trivial
    result += totalBattles * xpPerBattle * xpChain
    return result

def timeToLevel(secsPerBattle, secsFirstBattle, xpPerBattle, usingXPChain, 
        startLevel, endLevel, xpSoFar):
    totalXP = xpFromLevel(endLevel) - xpFromLevel(startLevel) - xpSoFar
    totalBattles = getBattlesFromXP(totalXP, xpPerBattle, usingXPChain)
    return getTimeFromBattles(totalBattles, secsPerBattle, secsFirstBattle)

def levelFromTime(secsPerBattle, secsFirstBattle, xpPerBattle,
        usingXPChain, totalSecs, startLevel):
    totalBattles = getBattlesFromTime(totalSecs, secsPerBattle, secsFirstBattle)
    totalXP = xpFromBattles(totalBattles, xpPerBattle, usingXPChain)
    return levelFromXP(totalXP, startLevel)

data = getData(sys.argv[1:])

SECS_PER_BATTLE = float(data["secsPerBattle"])
SECS_FIRST_BATTLE = float(data["secsFirstBattle"])
XP_PER_MONSTER = float(data["xpPerMonster"])
MONSTERS_PER_FIGHT = int(data["monstersPerFight"])
XP_CHAIN = bool(data["usingXPChain"])
NUM_FODDER = int(data["numFodder"])

XP_PER_BATTLE = XP_PER_MONSTER * MONSTERS_PER_FIGHT

currentLevel = int(data["currentLevel"])
desiredLevel = int(data["desiredLevel"])

# If user didn't supply levels on the command line
if (currentLevel == 0):
    currentLevel = int(input("Enter dragon's current level: "))
    desiredLevel = int(input("Enter desired level: "))

if not (currentLevel < desiredLevel):
    print("Your dragon has already reached that level!")
    sys.exit(0)

#pdb.set_trace()

XP_SO_FAR = int(data["xpSoFar"])
totalSecs = timeToLevel(SECS_PER_BATTLE, SECS_FIRST_BATTLE, XP_PER_BATTLE, 
        XP_CHAIN, currentLevel, desiredLevel, XP_SO_FAR)

print("Leveling the dragon(s) from " + str(currentLevel), end=" ")
print("to " + str(desiredLevel), end=" ")
print("will increase their value by ", end="")
print(str((payoutFromLevel(desiredLevel) - payoutFromLevel(currentLevel))))
if (NUM_FODDER > 1):
    print("each,", end=" ")
print("for a total value of " + str(payoutFromLevel(desiredLevel)
    * NUM_FODDER) + ".")

print("It will take " + str(totalSecs // 60) + " minutes and ", end="")
print(str((totalSecs % 60) // 1) + " seconds.")
print()

print("In that time, you could level fodder from 1 to ", end="")
fromOneTo = levelFromTime(SECS_PER_BATTLE, SECS_FIRST_BATTLE,  XP_PER_BATTLE, 
        XP_CHAIN, totalSecs, 1)
print(str(fromOneTo) + " for a payout of", end=" ")
print(str(payoutFromLevel(fromOneTo) * NUM_FODDER) + ".")


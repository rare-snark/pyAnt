#!/usr/bin/env python
import os
import time
import argparse
import random

# 0 = blank/white
# 1 = marked/black
# 2 = ant
# 3 = barrier
# face = orientation of the ant
#       white square turns 90 CW (left)
#       black square turns 90 CCW (right)
#       0 = right
#       1 = up
#       2 = left
#       3 = down

class MapHandler:
    def __init__(self, mapGrid: list[list[ list[list[int]]]]):
        self.mapGrid = mapGrid
        self.r = 0
        self.c = 0
        self.r0 = 0
        self.c0 = 0

    def expandMapGrid(self, dir: str, colony: list[dict], incidentAnt: dict):
        if dir == "^":
            self.r0 += 1
            for ant in colony:
                if ant != incidentAnt: ant["gr"] += 1
        elif dir == "<":
            self.c0 += 1
            for ant in colony:
                if ant != incidentAnt: ant["gc"] += 1
        expandMapGrid(self.mapGrid, dir)
    
def expandMapGrid(arr: list[list[ list[list[int]] ]], dir: str) -> None:
    exampleGrid = arr[0][0]
    r = len(exampleGrid)
    c = len(exampleGrid[0])
    if dir == ">":
        for row in arr:
            row.append([[0] * c for i in range (r)])
    elif dir == "<":
        for row in arr:
            row.insert(0, [[0] * c for i in range (r)])
    elif dir == "v":
        arr.append([[[0] * c for i in range (r)]])
        for j in range(len(arr[0])-1): arr[len(arr)-1].append([[0] * c for i in range (r)])
    elif dir == "^":
        arr.insert(0, [[[0] * c for i in range (r)]])
        for j in range(len(arr[1])-1): arr[0].append([[0] * c for i in range (r)])

def printMap(mh: MapHandler, ant: dict) -> None:
    mh.r = ant["gr"]
    mh.c = ant["gc"]
    map = mh.mapGrid[mh.r][mh.c]
    out = "spectating: {} | map: [{}, {}] | iter: {}\n".format(ant["id"], mh.r-mh.r0, mh.c-mh.c0, ant["age"])
    out += " "*(ant["c"]+2)+"v\n"
    TBBorder = " +"+("-"*len(map[0]))+"+"
    out += TBBorder + "\n"
    for r in range(len(map)):
        out += "{}¦".format(">" if r ==ant["r"] else " ")
        for c in range(len(map[0])):
            if r == ant["r"] and c == ant["c"]: out += "█"
            elif map[r][c] == 1: out += "░"
            else: out += " "
        out += "¦\n"
    out += TBBorder
    print(out)

def antAct(mh: MapHandler, ant: dict, colony: list[dict]) -> None:
    map = mh.mapGrid[ant["gr"]][ant["gc"]]
    ant["age"] += + 1
    #adjust orientation of ant, and flip the value of the space
    if (map[ant["r"]][ant["c"]] == 0):
        ant["face"] -= 1
        map[ant["r"]][ant["c"]] = 1
    else:
        ant["face"] += 1
        map[ant["r"]][ant["c"]] = 0
    if (ant["face"] == 4): ant["face"] = 0
    if (ant["face"] == -1): ant["face"] = 3
    #move ant
    #edge cases
    rLimit = len(map) - 1
    cLimit = len(map[0]) - 1
    gRLimit = len(mh.mapGrid)-1
    gCLimit = len(mh.mapGrid[0])-1
    if ant["face"] == 0:
        if ant["c"] == cLimit:
            ant["c"] = 0
            if ant["gc"] + 1 > gCLimit: mh.expandMapGrid(">", colony, ant)
            ant["gc"] += 1
        else:
            ant["c"] += 1
        return
    elif ant["face"] == 1:
        if ant["r"] == 0:
            ant["r"] = rLimit
            if ant["gr"] - 1 < 0: mh.expandMapGrid("^", colony, ant)
            else: ant["gr"] -= 1
        else:
            ant["r"] -= 1
        return
    elif ant["face"] == 2:
        if ant["c"] == 0:
            ant["c"] = cLimit
            if ant["gc"] - 1 < 0: mh.expandMapGrid("<", colony, ant)
            else: ant["gc"] -= 1
        else:
            ant["c"] -= 1
        return
    elif ant["face"] == 3:
        if ant["r"] == rLimit:
            ant["r"] = 0
            if ant["gr"] + 1 > gRLimit: mh.expandMapGrid("v", colony, ant)
            ant["gr"] += 1
        else:
            ant["r"] += 1
        return

def sendToFile(mh: MapHandler, fileName: str) -> None:
    f = open(fileName, "w")
    iter = []
    mapGrid = mh.mapGrid
    gridRowLimit = len(mapGrid)
    gridColLimit = len(mapGrid[0])
    exampleMap = mapGrid[0][0]
    rowLimit = len(exampleMap)
    colLimit = len(exampleMap[0])
    for gr in range(gridRowLimit):
        for r in range(rowLimit):
            for c in range(gridColLimit*colLimit):
                gc = (int) (c / colLimit)
                col = c % colLimit
                if col == 0: iter.append("¦")
                val = mapGrid[gr][gc][r][col]
                val = "█" if val == 1 else "░"
                iter.append(val)
            iter.append("\n")
        horiBorder = ((gridColLimit*colLimit)+gridColLimit)*["-"]
        horiBorder.append("\n")
        for i in range(gridColLimit):
            horiBorder[i*colLimit+i] = "+"
        # f.write("".join(horiBorder))
        iter += horiBorder
    f.write("".join(iter))
    f.close()

def ant():
    agp = argparse.ArgumentParser(description="CLI Langton's Ant simulator. Fills out terminal window. Written in python.")
    agp.add_argument(
        "-d",
        "--delay",
        default=0.1125,
        type=float,
        help="Seconds between iterations. Default: 0.1125"
    )
    agp.add_argument(
        "-si",
        "--skip-iterations",
        default=0,
        type=int,
        help="Iterations to skip before displaying the ant. Default: 0"
    )
    agp.add_argument(
        "-f",
        "--file",
        default="",
        type=str,
        help='Filename of file showing the final generated path. Make blank ("") to have no output. Default: ""'
    )
    agp.add_argument(
        "-cs",
        "--colony-size",
        default=1,
        type=int,
        choices=range(1,11),
        metavar="[1-10]",
        help="Number of ants deployed. Default: 1"
    )
    agp.add_argument(
        "-ss",
        "--spectator-switch",
        default=0,
        type = int,
        choices=range(0,1001),
        metavar="[0,1000]",
        help="number of iterations before switching which ant is spectated. 0 to disable. Default: 0."
    )
    args = agp.parse_args()

    size = os.get_terminal_size()
    c = size.columns - 3
    r = size.lines - 5

    map = [[0] * c for i in range(r)]
    
    mh = MapHandler([[map]])

    colony = []

    for i in range(args.colony_size):
        colony.append(
            {
                "r": (int)(r/2) + random.randint((int)(-r/4),(int)(r/4)),
                "c": (int)(c/2) + random.randint((int)(-c/4),(int)(c/4)),
                "face":random.randint(0,3),
                "age":1,
                "gr": 0,
                "gc": 0,
                "id": i
            }
        )

    spectated_ant = 0

    writing = args.file != ""

    try:
        while True:
            if args.spectator_switch != 0:
                if colony[len(colony)-1]["age"] % args.spectator_switch == 0:
                    spectated_ant = spectated_ant + 1 if spectated_ant != args.colony_size-1 else 0
            if colony[len(colony)-1]["age"] > args.skip_iterations:
                    printMap(mh, colony[spectated_ant])
                    time.sleep(args.delay)
            else:
                print("skipping iteration {}...".format(colony[len(colony)-1]["age"]))
            for ant in colony: antAct(mh, ant, colony)
            if writing: sendToFile(mh, args.file)
    except KeyboardInterrupt:
        print()
        if writing: sendToFile(mh, args.file)
        print("exiting...")


if __name__ == "__main__":
    ant()

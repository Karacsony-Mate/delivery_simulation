from raylibpy import *
import math
import heapq  # Prioritasi sor, kikuszoboli a listak rendezesenek szuksegesseget minden iteracioban


class Node:
    def __init__(self, x, y):
        self.x = x  # Node sor indexe
        self.y = y  # Node oszlop indexe
        self.g = float("inf")  # Utkoltseg a kezdoponttol a jelenlegi pontig
        self.h = 0  # Heurisztikus koltseg a jelenlegi ponttol a celpontig (Eukledeszi tavolsag)
        self.f = float("inf")  # Teljes koltsege (f = g + h)
        self.parent = None  # Szulo pont a visszakoveteshez es az utvonal letrehozasahoz
        self.walkable = True  # Fal-e a pont

    def __lt__(self, other):
        return self.f < other.f  # Azonos objektum relacios osszehasonlitasa

    def __eq__(self, other):
        return (
            isinstance(other, Node) and self.x == other.x and self.y == other.y
        )  # Azonos objektum egyenloseg checkje

    def __hash__(self):
        return hash((self.x, self.y))


grid = [
    [Node(x, y) for x in range(20)] for y in range(20)
]  # 20 * 20-as grid generalasa


def hDistance(nodeA, nodeB):
    h = math.sqrt(
        (nodeA.x - nodeB.x) ** 2 + (nodeA.y - nodeB.y) ** 2
    )  # Eukledeszi tavolsag
    # h = math.fabs(nodeA.x - nodeB.x) + math.fabs(nodeA.y - nodeB.y) # Manhattan tavolsag

    return h

def retracePath(
    startNode, endNode
):  # A megtalalt ut visszakovetese es eltarolasa hogy kilehessen majd rajzolni
    path = []
    currentNode = endNode  # Utolso nodetol visszafele
    while currentNode != startNode:
        path.append(currentNode)
        currentNode = currentNode.parent
    path.append(startNode)
    path.reverse()  # Megforditas, kezdoponttol a vegpontig
    return path


closedList = []  # Zart lista, meglatogatott Nodeokat taroljuk ide


def aStar(start, end):  # Fo algoritmus
    openList = (
        []
    )  # A kiterjesztett Nodeok ide kerulnek, mivel heapq mindig a legkisebb osszkoltsegu Node lesz a legelso helyen
    closedList.clear()  # Zarolt listat a contexten kivulre raktam szoval itt kell uriteni, az ok hogy az osszes meglatogatott cellat is lehessen vizualizalni

    start.g = 0  # A legelso Node koltseg 0 lesz, ugyanis ott allunk
    start.f = 0
    heapq.heappush(openList, start)  # Hozzaadjuk az openList-hez
    neighbor = [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]  # 8 iranybol a szomszedos cellak iranyvektorai
    # neighbor = [(1, 0), (0, -1), (0, 1), (-1, 0)] # 4 iranybol a szomszedos cellak iranyvektorai

    while len(openList) > 0:  # Amig kitudunk Nodeot terjeszteni, addig csinald
        currentNode = heapq.heappop(
            openList
        )  # Betoltjuk a heapq legelso elemet (kiterjesztjuk) es ezen dolgozunk
        closedList.append(currentNode)  # Meg lett latogatva, betoltjuk a closed listbe

        if (
            currentNode == end
        ):  # Ha elerjuk a cel Nodeot, atkuldi a kezdo es a jelenlegi pontot hogy visszavezesse az utat
            return retracePath(start, currentNode)

        for (
            newPosition
        ) in (
            neighbor
        ):  # Szomszedos Nodeok vizsgalasa a neighbor iranyvektorokat hasznalva
            nodePosition = (
                currentNode.x + newPosition[0],
                currentNode.y + newPosition[1],
            )  # Az aktualis Nodehoz hozzaadjuk az iranyvektort megkapva a megfelelo iranyba levo szomszedos nodeot
            if (
                nodePosition[0] > (len(grid) - 1)
                or nodePosition[0] < 0
                or nodePosition[1] > (len(grid[len(grid) - 1]) - 1)
                or nodePosition[1] < 0
            ):  # Ravizsgalunk hogy a Node ervenyes-e, benne van-e a negyzetracsos teruletben
                continue

            neighborNode = grid[nodePosition[1]][
                nodePosition[0]
            ]  # Ha ervenyes megkapjuk a szomszedos Nodeot
            if (
                not neighborNode.walkable or neighborNode in closedList
            ):  # Nem kell koltseget szamitani ha nem is mehetunk ra
                continue

            # Kiszamoljuk a legolcsobb szomszedos Nodeot f = g + h
            maybe_g = currentNode.g + hDistance(
                currentNode, neighborNode
            )  # 1 ha manhattan
            if maybe_g < neighborNode.g or neighborNode not in openList:
                neighborNode.g = maybe_g
                neighborNode.h = hDistance(neighborNode, end)
                neighborNode.f = neighborNode.g + neighborNode.h
                neighborNode.parent = currentNode  # A szomszedos cella "szuloje" a jelenlegi lesz, visszavezeteshez
                if neighborNode not in openList:
                    heapq.heappush(
                        openList, neighborNode
                    )  # Ha nem volt meg az openlistben a cella, hozzaadjuk


# start = grid[2][2]
# end = grid[7][11]

# path = aStar(start, end)
# Hardcodeolt test


# Fo program felepitese
def main():
    init_window(800, 800, "Pathfind")  # Ablak inicializacio
    set_target_fps(60)

    start = None
    end = None
    path = []

    while not window_should_close():  # Fo ciklus

        if is_mouse_button_pressed(MOUSE_RIGHT_BUTTON):
            mouseX = get_mouse_x()
            mouseY = get_mouse_y()

            gridPos = grid[math.floor(mouseY / 40)][math.floor(mouseX / 40)]
            
            gridPos.walkable = not gridPos.walkable

        if is_mouse_button_pressed(
            MOUSE_LEFT_BUTTON
        ):  # Bal klikkel lehet lehejezni a kezdo es vegpontot
            mouseX = get_mouse_x()
            mouseY = get_mouse_y()
            
            gridPos = grid[math.floor(mouseY / 40)][math.floor(mouseX / 40)] 
            
            if (start == None and gridPos.walkable ):
                start = gridPos  # Sketchy megoldas de amig a negyzethalo es az ablakfelbontasanak aranyos ertekeket adunk meg, addig pontosak lesznek a kapott indexek
            
            elif(end == None and gridPos.walkable):
                end = gridPos

        if (
            start != None and end != None
        ):  # Ha ervenyes a ket megadott pont meghivjuk az aStar() fuggvenyt
                path = aStar(start, end)
                start = None
                end = None
        # print(len(path) - 2) # ut hossza - a kezdo es vegpont


        # Rajzolas
        begin_drawing()
        clear_background(RAYWHITE)

        for row in grid:
            for node in row:
                if not node.walkable:
                    draw_rectangle(node.x * 40, node.y * 40, 40, 40, BLACK)  # Falak
                else:
                    draw_rectangle_lines(
                        node.x * 40, node.y * 40, 40, 40, BLACK
                    )  # "Negyzethalo" negyzetenket rajzoljuk ki

        for node in path:
            draw_rectangle(
                node.x * 40, node.y * 40, 40, 40, GREEN
            )  # Legrovidebb ut rajzolasa

        if len(path) > 0:
            draw_rectangle(path[0].x * 40, path[0].y * 40, 40, 40, BLUE)  # Kezdopont
            draw_rectangle(path[-1].x * 40, path[-1].y * 40, 40, 40, RED)  # Celpont

        # Csak azert hogy kattintas utan lassuk a kijelolt pontokat (De meg nem adtuk meg mind a kettot)
        if start != None:
            draw_rectangle(start.x * 40, start.y * 40, 40, 40, BLUE)

        if end != None:
            draw_rectangle(end.x * 40, end.y * 40, 40, 40, RED)

        end_drawing()

    close_window()


if __name__ == "__main__":
    main()

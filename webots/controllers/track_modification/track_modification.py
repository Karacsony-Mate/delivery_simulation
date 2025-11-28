from controller import Supervisor, Node

def modify_roads(node):
    """Rekurzívan bejárja a node gyermekeit és módosítja a Road node-okat"""
    if node is None:
        return

    # Ellenőrizzük, hogy ez Road típusú node-e
    if node.getField("road"):
        #print("Talált Road node:", node.getDef())
        node.getField("splineSubdivision").setSFInt32(5)

        # numberOfLanes mező beállítása 2-re
        lanes_field = node.getField("numberOfLanes")
        if lanes_field:
            lanes_field.setSFInt32(2)
            #print(node.getField("name"), "  -> numberOfLanes = 2")

        # elválasztó vonal színének állítása (RGB, 0..1 között)
        lines = node.getField("lines")
        
        #print(lines.getCount())
        lines_roadLine = lines.getMFNode(0)
        if lines_roadLine != "NoneType":
            lines_roadLine_Color = lines_roadLine.getField("color")
            lines_roadLine_Type = lines_roadLine.getField("type")
            lines_roadLine_Color.setSFColor([1.0, 1.0, 0.0])  # sárga
            lines_roadLine_Type.setSFString("dashed") # szagatott
            #print("  -> linesColor = sárga")
        #else:
            #proto_string = 'RoadLine { color 1 1 0 type "dashed" width 0.15 }'
            #lines.importMFNodeFromString(-1, proto_string)  # -1 → a végére szúrja
            

    # bejárjuk a gyerekeket is (pl. Group / Transform alatt)
    children_field = node.getField("children")
    if children_field:
        count = children_field.getCount()
        for i in range(count):
            child = children_field.getMFNode(i)
            modify_roads(child)


# Supervisor inicializálása
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

root = supervisor.getRoot()
children = root.getField("children")

# összes gyökérszintű node bejárása és módosítása
for i in range(children.getCount()):
    node = children.getMFNode(i)
    modify_roads(node)

#print("Minden Road node módosítva!")

# a változtatások érvényesítéséhez léptetni kell a szimulációt
while supervisor.step(timestep) != -1:
    pass

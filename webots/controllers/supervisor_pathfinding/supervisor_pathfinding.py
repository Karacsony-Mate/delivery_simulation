from controller import Supervisor
import os
import sys
import math

# Check required third-party packages
try:
    import numpy as np
    import networkx as nx
except ImportError as e:
    print("SUPERVISOR ERROR: missing dependency:", e)
    sys.exit(1)

# Load preprocessed map data from the integration folder
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "integration")
)
try:
    import map_data
except ImportError:
    print("SUPERVISOR ERROR: 'map_data.py' not found.")
    sys.exit()

# High-level configuration: start and goal junction IDs
START_JUNCTION = "-26791"
GOAL_JUNCTION = "-26980"

# Control loop parameters
TIME_STEP = 16
WAYPOINT_REACH_THRESHOLD = 3.0
MAX_SPEED = 25.0
MAX_STEER = 0.5
STEER_GAIN = -0.8

# Lane offset (meters to the right of the centerline)
LANE_OFFSET = 1.8

# Package delivery parameters and DEF names
PICKUP_DISTANCE = 4.5
DROPOFF_DISTANCE = 6.0
PACKAGE_DEF = "PACKAGE"
MARKER_DEF = "MARKER"


def euclidean(a, b):
    """Euclidean distance between 2D points using numpy."""
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


def normalize_angle(a):
    """Normalize angle to [-pi, pi]."""
    return (a + math.pi) % (2 * math.pi) - math.pi


def change_node_color(node):
    """Change the material color of a node to green (visual feedback)."""
    try:
        material = (
            node.getField("children")
            .getMFNode(0)
            .getField("appearance")
            .getSFNode()
            .getField("material")
            .getSFNode()
        )
        material.getField("diffuseColor").setSFColor([0, 1, 0])
        material.getField("transparency").setSFFloat(0.2)
    except Exception:
        pass


def shift_points(points, offset):
    """Shift a list of (x,y) centerline points to the right by `offset` meters.

    Uses a simple next/prev tangent for each point (no smoothing).
    """
    shifted = []
    n = len(points)
    for i, (x, y) in enumerate(points):
        if n == 1:
            tx, ty = 1.0, 0.0
        elif i == 0:
            tx = points[1][0] - x
            ty = points[1][1] - y
        elif i == n - 1:
            tx = x - points[i - 1][0]
            ty = y - points[i - 1][1]
        else:
            tx = points[i + 1][0] - points[i - 1][0]
            ty = points[i + 1][1] - points[i - 1][1]
        L = math.hypot(tx, ty) or 1.0
        # right-hand unit normal
        nx = ty / L
        ny = -tx / L
        shifted.append((round(x + nx * offset, 3), round(y + ny * offset, 3)))
    return shifted


def astar(start, goal, graph, coords):
    """Run A* using NetworkX on the provided graph and coordinates.

    Returns the list of junction ids from start to goal, or None.
    """
    print(f"SUPERVISOR: A* planning: {start} -> {goal}")

    G = nx.Graph()
    for u, neighbors in graph.items():
        if u not in coords:
            continue
        for v in neighbors:
            if v not in coords:
                continue
            w = euclidean(coords[u], coords[v])
            G.add_edge(u, v, weight=w)

    try:
        path = nx.astar_path(
            G,
            start,
            goal,
            heuristic=lambda u, v: euclidean(coords[u], coords[v]),
            weight="weight",
        )
        print(f"  -> SUPERVISOR A* path: {path}")
        return path
    except Exception as e:
        print("SUPERVISOR: networkx A* failed:", e)
        return None


def create_sphere_string(x, y, z, def_name, radius=0.3):
    """Return a Webots Transform DEF string for a red sphere at (x,y,z)."""
    return f"""
        DEF {def_name} Transform {{
            translation {x} {y} {z}
            children [
                Shape {{
                    appearance Appearance {{
                        material Material {{ diffuseColor 1 0 0 transparency 0.2 }}
                    }}
                    geometry Sphere {{ radius {radius} }}
                }}
            ]
        }}
        """


def main():
    # Initialize Supervisor and Webots scene root
    supervisor = Supervisor()
    root_node = supervisor.getRoot()
    world_children = root_node.getField("children")

    print("SUPERVISOR: Started.")

    # Plan a high-level path on the precomputed graph
    global_path_nodes = astar(
        START_JUNCTION,
        GOAL_JUNCTION,
        map_data.GLOBAL_GRAPH,
        map_data.JUNCTION_COORDS,
    )

    if not global_path_nodes:
        print("SUPERVISOR: No valid path, exiting.")
        return

    # Plot detailed waypoints (create visual spheres) and collect node refs
    print("SUPERVISOR: Plotting detailed path and preparing controller...")
    waypoints = []
    point_index = 0

    for i in range(len(global_path_nodes) - 1):
        path_key = (global_path_nodes[i], global_path_nodes[i + 1])
        if path_key in map_data.PATH_DETAILS:
            detailed_points = map_data.PATH_DETAILS[path_key]
            # Shift the centerline points to the right by LANE_OFFSET
            shifted_points = shift_points(detailed_points, LANE_OFFSET)
            for point in shifted_points:
                x, y = point[0], point[1]
                z = 0.5
                def_name = f"WAYPOINT_{point_index}"
                sphere_str = create_sphere_string(x, y, z, def_name)
                world_children.importMFNodeFromString(-1, sphere_str)
                node_ref = supervisor.getFromDef(def_name)
                if node_ref:
                    waypoints.append(
                        {"pos": (x, y), "node": node_ref, "visited": False}
                    )
                point_index += 1

    print(f"SUPERVISOR: Plotted {point_index} waypoints.")

    # Configure devices and locate the car node
    emitter = None
    try:
        emitter = supervisor.getDevice("path_emitter")
    except Exception:
        emitter = None

    car_node = supervisor.getFromDef("BMW")
    if not car_node:
        print("SUPERVISOR ERROR: 'DEF BMW' not found in world. Controller disabled.")
        return

    car_rotation_field = car_node.getField("rotation")

    # Package & marker setup
    package_node = supervisor.getFromDef(PACKAGE_DEF)
    marker_node = supervisor.getFromDef(MARKER_DEF)
    has_package = False
    delivered = False

    # Set marker initial color to red (if available)
    marker_color_field = None
    if marker_node:
        try:
            marker_color_field = marker_node.getField("color")
            marker_color_field.setSFColor([1, 0, 0])
        except Exception:
            marker_color_field = None

    # Main control loop: sequence states -> to_package -> follow_path -> to_marker
    current_wp_index = 0
    state = "to_package" if package_node is not None else "follow_path"
    print(f"SUPERVISOR: State -> {state}")

    while supervisor.step(TIME_STEP) != -1:
        if current_wp_index >= len(waypoints) and state != "to_marker":
            if emitter:
                emitter.send("0.0,0.0".encode("utf-8"))
            continue

        car_pos_3d = car_node.getPosition()
        car_pos = (car_pos_3d[0], car_pos_3d[1])

        orientation = car_node.getOrientation()
        car_yaw = math.atan2(orientation[3], orientation[0])

        # Read package/marker positions when available
        try:
            pkg_pos = package_node.getPosition() if package_node is not None else None
        except Exception:
            pkg_pos = None
        try:
            marker_pos = marker_node.getPosition() if marker_node is not None else None
        except Exception:
            marker_pos = None

        # Pickup handling: if in to_package state, check for pickup proximity
        if state == "to_package" and not has_package and pkg_pos is not None:
            if euclidean(car_pos, (pkg_pos[0], pkg_pos[1])) < PICKUP_DISTANCE:
                try:
                    package_node.getField("translation").setSFVec3f([0, 0, -10])
                except Exception:
                    pass
                has_package = True
                state = "follow_path"
                print(f"SUPERVISOR: State -> {state}")
                print("SUPERVISOR: Package picked up")

        # Dropoff handling: only after following path we go to marker
        if state == "to_marker" and has_package and marker_pos is not None:
            if euclidean(car_pos, (marker_pos[0], marker_pos[1])) < DROPOFF_DISTANCE:
                has_package = False
                delivered = True
                if marker_color_field:
                    try:
                        marker_color_field.setSFColor([0, 1, 0])
                    except Exception:
                        pass
                state = "done"
                print(f"SUPERVISOR: State -> {state}")
                print("SUPERVISOR: Package delivered")

        # Choose active target depending on state
        if state == "to_package":
            # target is the package location
            if pkg_pos is None:
                # no package position available: fallback to first waypoint
                if len(waypoints) == 0:
                    continue
                target_pos = waypoints[0]["pos"]
            else:
                target_pos = (pkg_pos[0], pkg_pos[1])
        elif state == "follow_path":
            # follow the precomputed waypoints
            # Mark visited waypoints and update the current index
            for i in range(current_wp_index, len(waypoints)):
                wp = waypoints[i]
                dist = euclidean(car_pos, wp["pos"])
                if dist < WAYPOINT_REACH_THRESHOLD:
                    if not wp["visited"]:
                        wp["visited"] = True
                        change_node_color(wp["node"])
                    if i >= current_wp_index:
                        current_wp_index = i + 1

            if current_wp_index >= len(waypoints):
                # finished the path -> go to marker (if package carried)
                state = (
                    "to_marker" if has_package and marker_pos is not None else "done"
                )
                print(f"SUPERVISOR: State -> {state}")
                continue

            target_wp = waypoints[current_wp_index]
            target_pos = target_wp["pos"]
        elif state == "to_marker":
            # target is the delivery marker
            if marker_pos is None:
                continue
            target_pos = (marker_pos[0], marker_pos[1])
        else:
            # done or unknown state: stop sending commands
            if emitter:
                emitter.send("0.0,0.0".encode("utf-8"))
            continue

        dx = target_pos[0] - car_pos[0]
        dy = target_pos[1] - car_pos[1]
        desired_yaw = math.atan2(dy, dx)
        yaw_error = normalize_angle(desired_yaw - car_yaw)

        steer = STEER_GAIN * yaw_error
        steer = max(-MAX_STEER, min(MAX_STEER, steer))

        if emitter:
            msg = f"{steer},{MAX_SPEED}".encode("utf-8")
            emitter.send(msg)


if __name__ == "__main__":
    main()

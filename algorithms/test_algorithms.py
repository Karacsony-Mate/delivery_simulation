import pytest
from Python_Pathfind import Node, grid, aStar, hDistance


def test_node_creation():
    """Test that Node objects are created with correct initial values"""
    node = Node(1, 2)
    assert node.x == 1
    assert node.y == 2
    assert node.g == float("inf")
    assert node.h == 0
    assert node.f == float("inf")
    assert node.parent is None
    assert node.walkable is True


def test_node_comparison():
    """Test Node comparison operations"""
    node1 = Node(1, 1)
    node2 = Node(1, 1)
    node3 = Node(2, 2)

    # Test equality
    assert node1 == node2
    assert node1 != node3

    # Test less than (based on f value)
    node1.f = 10
    node2.f = 20
    assert node1 < node2


def test_heuristic_distance():
    """Test the heuristic distance calculation"""
    node1 = Node(0, 0)
    node2 = Node(3, 4)
    # Expected Euclidean distance is 5 (3-4-5 triangle)
    assert abs(hDistance(node1, node2) - 5.0) < 0.0001


def test_path_finding_direct():
    """Test pathfinding with no obstacles"""
    # Reset any walls in the grid
    for row in grid:
        for node in row:
            node.walkable = True

    start = grid[0][0]
    end = grid[2][2]

    path = aStar(start, end)

    assert path is not None
    assert len(path) > 0
    assert path[0] == start
    assert path[-1] == end


def test_path_finding_with_wall():
    """Test pathfinding with obstacles"""
    # Reset and create a simple wall
    for row in grid:
        for node in row:
            node.walkable = True

    # Create a wall
    grid[1][1].walkable = False

    start = grid[0][0]
    end = grid[2][2]

    path = aStar(start, end)

    assert path is not None
    assert len(path) > 0
    assert path[0] == start
    assert path[-1] == end
    # Path should not contain the wall node
    assert grid[1][1] not in path


def test_path_finding_impossible():
    """Test pathfinding when no path is possible"""
    # Reset grid
    for row in grid:
        for node in row:
            node.walkable = True

    # Create a wall surrounding the end
    grid[1][1].walkable = False
    grid[1][2].walkable = False
    grid[1][3].walkable = False
    grid[2][1].walkable = False
    grid[3][1].walkable = False
    grid[2][3].walkable = False
    grid[3][2].walkable = False
    grid[3][3].walkable = False

    start = grid[0][0]
    end = grid[2][2]

    path = aStar(start, end)

    # When no path is possible, the algorithm should return an empty path
    assert path is None or len(path) == 0


def test_grid_boundaries():
    """Test that the algorithm handles grid boundaries correctly"""
    start = grid[0][0]
    end = grid[19][19]  # Should be the corner of your 20x20 grid

    path = aStar(start, end)

    assert path is not None
    assert len(path) > 0
    assert path[0] == start
    assert path[-1] == end

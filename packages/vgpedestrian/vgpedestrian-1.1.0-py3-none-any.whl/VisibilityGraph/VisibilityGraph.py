from DataStructures.LineWay import LineWay
import sys

""""<<<<<<< HEAD
=======

>>>>>>> 54ae4f28c0eb74936da113704690fa5ca5ef2ccc"""

class VisibilityGraph:
    """Applies the Visiblity Graph Algorithm to the input OpenSpaces

    Args:
        openspace_list(list<OpenSpace>): List containing polygons, parsed from osm-input-file

    Attributes:
        max_int(String):                        Counter for IDs of new ways
        openspace_list(List<OpenSpace>):        OpenSpaces to apply VG on
        new_ways(List<Way>):                    List for generated ways
    """

    def __init__(self, openspace_list):
        self.max_int = sys.maxsize
        self.openspace_list = openspace_list
        self.new_ways = []

    def create(self):
        """ Execute the Visibility Graph Algorithm
        Returns:
            List of generated ways
        """
        attributes = {"highway": "pedestrian"}

        try:
            for openspace in self.openspace_list:
                outer = openspace.outer_ways
                openspace.create_polygon_with_holes()

                # create ways between all nodes on the outer ring of the polygon
                #i,b: counter to avoid double ways

                i = 0
                for node_from in outer[:(len(outer) - 1)]:
                    for node_to in outer[i:(len(outer) - 1)]:
                        nodes = []
                        nodes.append(node_from)
                        nodes.append(node_to)

                        # generate new way with wayIds
                        new_way = LineWay(self.handle_id(), nodes, attributes)
                        # test for intersection with holes of polygon
                        new_way.create_line()
                        try:
                            if openspace.polygon_with_holes.contains(new_way.line):
                                self.new_ways.append(new_way)
                        except Exception as e:
                            sys.stderr.write("Could not perfom. Likely caused by invalid geometry\n")
                            raise

                    i = i + 1

                i = 0
                for hole in openspace.inner_ways:
                    # create ways between all nodes on inner rings and all nodes on the outer ring
                    b = 0
                    for node_from in hole.nodes[:len(hole.nodes)-1]:
                        for node_to in outer[:len(outer)-1]:
                            nodes = []
                            nodes.append(node_from)
                            nodes.append(node_to)

                            # generate new way with wayIds
                            new_way = LineWay(self.handle_id(), nodes, attributes)
                            # test for intersection with holes of polygon
                            new_way.create_line()
                            try:
                                if openspace.polygon_with_holes.contains(new_way.line):
                                    self.new_ways.append(new_way)
                            except Exception as e:
                                sys.stderr.write("Could not perfom. Likely caused by invalid geometry\n")
                                raise

                        # create ways between all nodes on inner rings to all other nodes on inner rings
                        for hole_to in openspace.inner_ways[i:]:
                            # decision: If  hole_to is equal to hole -> a counter is necessary to avoid redundant ways
                            if hole_to == openspace.inner_ways[i]:
                                for node_to in hole_to.nodes[b:len(hole_to.nodes)-1]:
                                    nodes = []
                                    nodes.append(node_from)
                                    nodes.append(node_to)

                                    # generate new way with wayIds
                                    new_way = LineWay(self.handle_id(), nodes, attributes)
                                    # test for intersection with holes of polygon
                                    new_way.create_line()
                                    try:
                                        if openspace.polygon_with_holes.contains(new_way.line):
                                          self.new_ways.append(new_way)
                                    except Exception as e:
                                        sys.stderr.write("Could not perfom. Likely caused by invalid geometry\n")
                                        raise
                                b = b + 1
                            else:
                                for node_to in hole_to.nodes[:len(hole_to.nodes)-1]:
                                    nodes = []
                                    nodes.append(node_from)
                                    nodes.append(node_to)

                                    # generate new way with wayIds
                                    new_way = LineWay(self.handle_id(), nodes, attributes)
                                    # test for intersection with holes of polygon
                                    new_way.create_line()
                                    try:
                                        if openspace.polygon_with_holes.contains(new_way.line):
                                          self.new_ways.append(new_way)
                                    except Exception as e:
                                        sys.stderr.write("Could not perfom. Likely caused by invalid geometry\n")
                                        raise
                    i = i + 1

                # create ways on all inner rings
                for hole in openspace.inner_ways:
                    new_way = LineWay(self.handle_id(), hole.nodes, attributes)
                    # test for intersection has to be omitted
                    new_way.create_line()
                    self.new_ways.append(new_way)

            return self.new_ways

        except Exception as e:
            sys.stderr.write("create additional ways failed \n")
            raise


    def handle_id(self):
        """Generates ids for newly created ways
            As graphhopper uses long to store the information,
            we cannot concat the old and the new id, so we start from the max
            int.

            Note: This bears the risk of potentially duplicating existing ids

            Returns:
                 ID for generated way
        """
        self.max_int = self.max_int - 1
        return str(self.max_int)

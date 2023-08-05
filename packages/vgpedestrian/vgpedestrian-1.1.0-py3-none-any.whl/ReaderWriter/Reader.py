import xml.etree.ElementTree as ET
import sys
from xml.etree.ElementTree import ParseError

from DataStructures.LineWay import LineWay
from DataStructures.AreaWay import AreaWay
from DataStructures.Node import Node
from DataStructures.OpenSpace import OpenSpace


class Reader:
    """Read an osm file and create the OmsObjects

    The key for all dictionaries is the id from the input

    Attributes:
        node_dict(dict<Node>):      Nodes parsed from input
        lineway_dict(dict<LineWay): Ways, that are not areas
        area_dict(dict<AreaWay):    Areas, not pedestrian (possible obstacles)
        open_space_dict(dict<OS>):  Areas parsed from input

    """

    def __init__(self):
        self.node_dict = {}
        self.open_space_dict = {}
        self.lineway_dict = {}
        self.area_dict = {}

    def parse_xml(self, filepath):
        try:
            tree = ET.parse(filepath)
        except FileNotFoundError as e:
            raise(e)
        except ParseError as e:
            raise(e)

        root = tree.getroot()

        for elem in root.findall('*'): #komplettes XML Zeile für Zeile durchlaufen

            #######################
            # N    O    D   E   S #
            #######################
            if elem.tag == "node": #wenn Knoten "node"
                attributes = {}
                for child_elem in elem:
                    if child_elem.tag == "tag":
                        try:
                            attributes[child_elem.attrib["k"]] = child_elem.attrib["v"]
                        except Exception as e:
                            sys.stderr.write("Could not append tag for node.\n")
                            sys.stderr.write(f"{e}")
                try:
                    self.node_dict[elem.attrib["id"]] = (Node(elem.attrib["id"],
                        elem.attrib["lat"], elem.attrib["lon"], attributes)
                    )
                except Exception as e:
                    sys.stderr.write("Node could not be added\n")
                    sys.stderr.write(f"{e}")


            #######################
            #  W    A    Y     S  #
            #######################
            elif elem.tag == "way":

                is_area = False
                is_pedestrian = False
                way_id = elem.attrib["id"]
                nodes_of_way = []
                attributes = {}

                for child_elem in elem:
                    if child_elem.tag == "nd":
                        node_key = child_elem.attrib["ref"]
                        target_node = self.node_dict[node_key] #Node suchen in nodedict und speichern
                        nodes_of_way.append(target_node)

                    if child_elem.tag == "tag":
                        try:
                            attributes[child_elem.attrib["k"]] = child_elem.attrib["v"]
                        except Exception as e:
                            sys.stderr.write("Could not append tag for way.\n")
                            sys.stderr.write(f"{e}")

                        if self.elem_is_pedestrian(child_elem): #überprüfe nur in tag elementen ob pedestrian
                            is_pedestrian=True

                        if self.elem_is_area_way(child_elem): #überprüfe nur in tag element ob child
                            is_area=True

                #Needed for ways that are "areas" but not have an area tag
                #Most importantly inner und outer members of relations
                if nodes_of_way[0] == nodes_of_way[-1]:
                    is_area = True

                if is_area:
                    try:
                        new_area = AreaWay(way_id, nodes_of_way, attributes)
                        self.area_dict[way_id] = new_area
                    except Exception as e:
                        sys.stderr.write("Area could not be added.\n")
                        sys.stderr.write(f"{e}")
                    if is_pedestrian:
                        #Basic open space that has no holes
                        try:
                            new_space = OpenSpace(way_id, [new_area], [], attributes)
                            self.open_space_dict[way_id] = new_space
                        except Exception as e:
                            sys.stderr.write("Simple OpenSpace could not be added.\n")
                            sys.stderr.write(f"{e}")
                elif not is_area:
                    #Simple way that we only need to check for dupliactes
                    #TODO: Possibly take only not is_area and is_pedestrian
                    try:
                        new_line = LineWay(way_id, nodes_of_way, attributes)
                        self.lineway_dict[way_id] = new_line
                    except Exception as e:
                        sys.stderr.write("LineWay object could not be added.\n")
                        sys.stderr.write(f"{e}")

            #######################
            #  R   E    L     S   #
            #######################
            elif elem.tag == "relation":

                is_multipolygon = False
                is_pedestrian = False
                is_area = False

                inner_members = []
                outer_members = []
                attributes = {}

                for child_elem in elem:
                    if child_elem.tag == "member":
                        # Die OSM enthält selten keine Knoten auf die referenziert wird, Fehler in der XML?
                        if child_elem.attrib["role"] == "inner" and (child_elem.attrib["ref"] in self.area_dict):
                            inner_members.append(self.area_dict[child_elem.attrib["ref"]])
                        elif child_elem.attrib["role"] == "outer" and (child_elem.attrib["ref"] in self.area_dict):
                            outer_members.append(self.area_dict[child_elem.attrib["ref"]])

                    elif child_elem.tag == "tag":
                        try:
                            attributes[child_elem.attrib["k"]] = child_elem.attrib["v"]
                        except Exception as e:
                            sys.stderr.write("Could not append tag for relation\n")
                            sys.stderr.write(f"{e}")

                    if self.elem_is_pedestrian(child_elem):
                        is_pedestrian = True
                    if self.elem_is_area_way(child_elem):
                        is_area = True
                    if self.elem_is_multipolygon(child_elem):
                        is_multipolygon = True

                if is_pedestrian and (is_area or is_multipolygon):
                    #OpenSpace from relation with holes
                    try:
                        space = OpenSpace(elem.attrib['id'], outer_members, inner_members, attributes)
                        self.open_space_dict[space.id] = space
                    except Exception as e:
                        sys.stderr.write("Relation could not be added to OpenSpace\n")
                        sys.stderr.write(f"{e}")

        return self.open_space_dict



    def get_data(self):
        return [self.node_dict,
                self.open_space_dict,
                self.lineway_dict,
                self.area_dict]

        # Helper classes
    def elem_is_area_way(self, element):
        return "k" in element.attrib and element.attrib["k"] == "area"

    def elem_is_pedestrian(self, element):
        return "k" in element.attrib and element.attrib[
            "k"] == "highway" and "v" in element.attrib and element.attrib["v"] == "pedestrian"

    def elem_is_multipolygon(self, element):
        return "k" in element.attrib and element.attrib[
            "k"] == "type" and "v" in element.attrib and element.attrib["v"] == "multipolygon"

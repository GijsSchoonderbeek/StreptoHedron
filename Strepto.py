"""
Python script to be used with Freecad to draw Streptohedron
Gijs
25-5-2019
"""
import math
import FreeCAD
import Part
#from FreeCAD import Base
#from pivy import coin
import DraftVecUtils

def sphere():
    """ Function to make the fases
    """
    sides = 12        # sides per ring
    rings = 3         # Nof ring on the torus
    width = 250       # approximately final diameter in mm
    height = width
    App.Console.PrintMessage("\nDraw streptohedron based on " + str(sides) + " Sides, " \
                             + str(sides*(rings - 1) * 2) + " Faces \n")
    total_length = 0
    ring_loc = []
    v_cross_base = FreeCAD.Vector(height / 2, 0, 0)

    cor_factor = 1 / math.cos(2 * math.pi / (sides * 2))
    stri = "cor factor = {:2.2f} \n".format(cor_factor)
    App.Console.PrintMessage(stri)

    for ring_cnt in range(rings + 1):
        r_angle = ((ring_cnt) * (math.pi / rings)) + (math.pi / 2)
        vector_to_loc = DraftVecUtils.rotate(v_cross_base, -r_angle, \
                        FreeCAD.Vector(0, 1, 0)).scale(cor_factor, cor_factor, 1)
        ring_loc.append(vector_to_loc)

    vector = []
    for ring_cnt in range(rings + 1):
        ring_vertices = []
        base_vector = ring_loc[ring_cnt]
        for cnt in range(0, sides):
            if (ring_cnt % 2) == 0:
                r_angle = ((cnt + 0.5) * (2 * math.pi / sides))
            else:
                r_angle = (cnt * (2 * math.pi / sides))
            ring_vertices.append(DraftVecUtils.rotate(base_vector, r_angle))
        vector.append(ring_vertices)

    # Make the wires/faces
    faces = []
    for ring in range(rings):
        if ring == 0:
            for cnt in range(sides):
                vec_0 = vector[ring][cnt]
                vec_1 = vector[ring + 1][(cnt) % sides]
                vec_2 = vector[(ring + 1)][(cnt + 1) % sides]
                faces.append(make_face(vec_0, vec_1, vec_2))
        elif ring == (rings - 1):
            for cnt in range(sides):
                vec_0 = vector[ring][cnt]
                vec_1 = vector[ring][(cnt + 1) % sides]
                vec_2 = vector[(ring + 1)][cnt]
                faces.append(make_face(vec_0, vec_1, vec_2))
        else:
            for cnt in range(sides):
                vec_0 = vector[ring][cnt]
                # % sides --> Start at 0 when round
                vec_1 = vector[ring][(cnt + 1) % sides]
                # % 2 --> when odd ring use next vertex on next ring
                vec_2 = vector[(ring + 1) % rings][(cnt + 1 - (ring % 2)) % sides]
                # Up facing Triangle
                faces.append(make_face(vec_0, vec_1, vec_2))
                # % rings --> start at 0 when round
                vec_0 = vector[(ring + 1) % rings][cnt]
                # % sides --> Start at 0 when round
                vec_1 = vector[(ring + 1) % rings][(cnt + 1) % sides]
                # when even ring use next vertex on previous ring
                vec_2 = vector[ring][(cnt + (ring % 2)) % sides]
                # Down facing Triangle
                faces.append(make_face(vec_0, vec_1, vec_2))
        edge_lengths = []
        for edge_cnt in range(3):
            edge_lengths.append(round(faces[-1].Edges[edge_cnt].Length, 1))
            App.Console.PrintMessage("Length Edge nr. " + str(edge_cnt) + \
                                     " : " + str(edge_lengths[-1]) + " mm \n")
        edge_lengths.sort()
        angle = 360.0 * math.asin((edge_lengths[0] / 2)/edge_lengths[1]) / math.pi
        stri = "Angle : {:3.1f}° --> miter: {:3.1f}°\n".format(angle,\
                90-(angle)/2)
        App.Console.PrintMessage(stri)
        vns1 = faces[-1].normalAt(0, 0)
        vns2 = faces[-2].normalAt(0, 0)
        if 0 < ring < (rings - 1):
            angle_1_2 = 180 - round(math.degrees(vns1.getAngle(vns2)), 2)
        else:
            angle_1_2 = round(math.degrees(vns1.getAngle(vns2)), 2)
        stri = "Ring : {:2d} Angle faces {:2.2f} ° --> SAW angle: {:2.2f} °\n".format(
            ring, angle_1_2, angle_1_2 / 2)
        App.Console.PrintMessage(stri)
        total_length += (sides + 1) * edge_lengths[0]
    for ring_cnt in range(rings):
        if ring_cnt == 0:
            vns1 = faces[0].normalAt(0, 0)
            vns2 = faces[sides].normalAt(0, 0)
            angle_1_2 = 180 - round(math.degrees(vns1.getAngle(vns2)), 1)
            stri = "Angle faces Ring {:2d} - {:2d} {:2.2f}° --> SAW angle : {:2.2f}° \n".format(
                ring_cnt, ring_cnt + 1, angle_1_2, angle_1_2 / 2)
            App.Console.PrintMessage(stri)
        if 0 < ring_cnt < (rings - 1):
            vns1 = faces[sides + (2 * sides * (ring_cnt - 1)) + 1].normalAt(0, 0)
            vns2 = faces[sides + (2 * sides * ((ring_cnt) % rings))].normalAt(0, 0)
            angle_1_2 = 180 - round(math.degrees(vns1.getAngle(vns2)), 1)
            stri = "Angle faces Ring {:2d} - {:2d} {:2.2f}° --> SAW angle : {:2.2f}° \n".format(
                ring_cnt, ring_cnt+1, angle_1_2, angle_1_2 / 2)
            App.Console.PrintMessage(stri)
    stri = "Total Length wood {:3.2f} m \n".format(total_length / 1000)
    App.Console.PrintMessage(stri)

    shell = Part.makeShell(faces)
    solid = Part.makeSolid(shell)
    return solid

def make_face(vec_1, vec_2, vec_3):
    """
    Function to make the fases
    """
    wire = Part.makePolygon([vec_1, vec_2, vec_3, vec_1])
    face = Part.Face(wire)
    return face

def make_sphere():
    """
    Function to make sphere in FreeCAD
    """
    FreeCAD.newDocument()
    generated_sphere = sphere()
    Part.show(generated_sphere)

make_sphere()
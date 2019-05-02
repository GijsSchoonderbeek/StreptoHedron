
import FreeCAD, Part, math
from FreeCAD import Base
from pivy import coin
import DraftVecUtils
import math
faces=[]


 
def sphere():
	global faces
	Sides=12        # sides per ring
	Rings=3			# Nof ring on the torus
	Width=250 		# approximately final diameter in mm
	Height=Width
	App.Console.PrintMessage("\nDraw streptohedron based on " + str(Sides) + " Sides, " + str(Sides*(Rings-1)*2) +" Faces \n")
	Total_lenght=0
	ring_loc = []
	v_cross=[]
	v_cross_base = FreeCAD.Vector(Height/2,0,0)

	cor_factor = 1/math.cos(2*math.pi/(Sides*2))
	stri="cor factor = {:2.2f} \n".format(cor_factor)
	App.Console.PrintMessage(stri)
	
	for ring_cnt in range(Rings+1):
		r_angle =((ring_cnt)*(math.pi/Rings))+(math.pi/2)
		vector_to_loc = DraftVecUtils.rotate(v_cross_base,-r_angle,FreeCAD.Vector(0,1,0)).scale(cor_factor,cor_factor,1) 
		ring_loc.append(vector_to_loc)
	
	v=[]
	for ring_cnt in range(Rings+1):
		vr=[]
		base_vector = ring_loc[ring_cnt]
		for cnt in range(0,Sides):
			if (ring_cnt % 2)==0:
				r_angle=((cnt+0.5)*(2*math.pi/Sides))
			else:
				r_angle=(cnt*(2*math.pi/Sides))
			vr.append(DraftVecUtils.rotate(base_vector,r_angle))
		v.append(vr)
		
	# Make the wires/faces
	f=[]
	for ring in range(Rings):
		if ( ring == 0):
			for cnt in range(Sides):
				v0 = v[ring][cnt]
				v1 = v[ring+1][(cnt)%Sides]  					
				v2 = v[(ring+1)][(cnt+1)%Sides]	
				f.append(make_face(v0,v1,v2)) 					
		elif ( ring == Rings-1):
			for cnt in range(Sides):
				v0 = v[ring][cnt]
				v1 = v[ring][(cnt+1)%Sides]  					
				v2 = v[(ring+1)][cnt]	
				f.append(make_face(v0,v1,v2)) 					
		else:
			for cnt in range(Sides):
				v0=v[ring][cnt]
				v1 = v[ring][(cnt+1)%Sides]  					# % Sides --> Start at 0 when round
				v2 = v[(ring+1)%Rings][(cnt+1-(ring%2))%Sides]	# % 2 --> when odd ring use next vertex on next ring
				f.append(make_face(v0,v1,v2)) 					# Up facing Triangle
				v0 = v[(ring+1)%Rings][cnt]						# % Rings --> start at 0 when round
				v1 = v[(ring+1)%Rings][(cnt+1)%Sides]			# % Sides --> Start at 0 when round
				v2 = v[ring][(cnt+(ring%2))%Sides]				# when even ring use next vertex on previous ring
				f.append(make_face(v0,v1,v2))  					# Down facing Triangle
		edge_lengths=[]
		for edge_cnt in range(3):				
			edge_lengths.append(round(f[-1].Edges[edge_cnt].Length,1))
			App.Console.PrintMessage("Length Edge nr. " + str(edge_cnt) + " : " + str(edge_lengths[-1]) + " mm \n")
		edge_lengths.sort()
		angle = 360.0 * math.asin((edge_lengths[0]/2)/edge_lengths[1])/math.pi
		stri = "Angle : {:3.1f}° --> miter: {:3.1f}°\n".format(angle, 90-(angle)/2)
		App.Console.PrintMessage(stri)
		vns1 = f[-1].normalAt(0,0)
		vns2 = f[-2].normalAt(0,0)
		if 0 < ring < (Rings-1):
			Angle_1_2=180-round(math.degrees(vns1.getAngle(vns2)),2)
		else:
			Angle_1_2=round(math.degrees(vns1.getAngle(vns2)),2)
		stri = "Ring : {:2d} Angle faces {:2.2f} ° --> SAW angle: {:2.2f} °\n".format(ring, Angle_1_2, Angle_1_2/2)
		App.Console.PrintMessage(stri)
		Total_lenght += (Sides+1)*edge_lengths[0]
	for ring_cnt in range(Rings):
		if ring_cnt ==0:
			vns1 = f[0].normalAt(0,0)
			vns2 = f[Sides].normalAt(0,0)
			Angle_1_2=180-round(math.degrees(vns1.getAngle(vns2)),1)
			stri = "Angle faces Ring {:2d} - {:2d} {:2.2f}° --> SAW angle : {:2.2f}° \n".format(ring_cnt, ring_cnt+1, Angle_1_2, Angle_1_2/2)
			App.Console.PrintMessage(stri)
		if 0 < ring_cnt < (Rings-1):
			vns1 = f[Sides+(2*Sides*(ring_cnt-1))+1].normalAt(0,0)
			vns2 = f[Sides+(2*Sides*((ring_cnt)%Rings))].normalAt(0,0)
			Angle_1_2=180-round(math.degrees(vns1.getAngle(vns2)),1)
			stri = "Angle faces Ring {:2d} - {:2d} {:2.2f}° --> SAW angle : {:2.2f}° \n".format(ring_cnt, ring_cnt+1, Angle_1_2, Angle_1_2/2)
			App.Console.PrintMessage(stri)
	stri = "Total Length wood {:3.2f} m \n".format(Total_lenght/1000)
	App.Console.PrintMessage(stri)
	faces=f
	
	shell=Part.makeShell(f)
	solid=Part.makeSolid(shell)
	Shape = solid
	return Shape

def make_face(v1,v2,v3):									#Function to make the faces of the triangles
	wire = Part.makePolygon([v1,v2,v3,v1])
	face = Part.Face(wire)
	return face

def make_sphere():											#Function to make the Torus
	FreeCAD.newDocument()
	a = sphere()
	Part.show(a)

make_sphere()

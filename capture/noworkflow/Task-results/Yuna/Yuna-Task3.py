import numpy as np

# --- Angle function --- 
def getangle(at1, at2, at3, lol):
	try:
		atom1 = array([float(lol[at1][1]), float(lol[at1][2]), float(lol[at1][3])])
		atom2 = array([float(lol[at2][1]), float(lol[at2][2]), float(lol[at2][3])])
		atom3 = array([float(lol[at3][1]), float(lol[at3][2]), float(lol[at3][3])])
		# making appropriate vectors and normals 
		vector1 = atom1-atom2
		vector2 = atom3-atom2
		angle = arccos(dot(vector1,vector2)/(linalg.norm(vector1)*linalg.norm(vector2)))
		#print degrees(angle)
		return degrees(angle)
	except:
		return 0.000000

# --- Dihedral angle function ---
def getdihedral(at1, at2, at3, at4, lol):
	try:
		# put positions in array
		atom1 = array([float(lol[at1][1]), float(lol[at1][2]), float(lol[at1][3])])
		atom2 = array([float(lol[at2][1]), float(lol[at2][2]), float(lol[at2][3])])
		atom3 = array([float(lol[at3][1]), float(lol[at3][2]), float(lol[at3][3])])
		atom4 = array([float(lol[at4][1]), float(lol[at4][2]), float(lol[at4][3])])
		# making appropriate vectors and normals 
		vector1 = atom2-atom1
		vector2 = atom3-atom2
		plane1 = cross(vector1,vector2)
		vector3 = atom2-atom3
		vector4 = atom4-atom3
		plane2 = cross(vector3,vector4)
		# finding dihedral angle
		dihedral = arccos(-dot(plane1,plane2)/(linalg.norm(plane1)*linalg.norm(plane2)))
		# checking the sign of the dihedral then displaying result
		if dot(plane1,vector4) > 0:
			#print degrees(dihedral)
			return  degrees(dihedral)
		else:
			#print -degrees(dihedral)
			return - degrees(dihedral)
	except:
		return 0	

# --- get the distance, angle and dihedrals for a Z-matrix --- 
def getzmat(i):
	line = []
	line.append(getElementName(ifilelol[i+2][0]))
	if i > 0:
		line.append(i)
		dist = getdistance(i+1, i+2, ifilelol)
		line.append(dist)
	if i > 1:
		line.append(i-1)
		angle = getangle(i, i+1, i+2, ifilelol)
		line.append(angle)
	if i > 2:
		line.append(i-2)
		dihedral = getdihedral(i-1, i, i+1, i+2, ifilelol)
		line.append(dihedral)
	line.append(-1)
	line.append(-1)
	line.append(-1)
	line.append(-1)
	line.append(-1)
	line.append(-1)
	line.append("\n")
	return line

def readxyz(filename):
    xyzf = open(filename, 'r')
    xyzarr = np.zeros([1, 3])
    atomnames = []
    if not xyzf.closed:
        # Read the first line to get the number of particles
        npart = int(xyzf.readline())
        # and next for title card
        title = xyzf.readline()

        # Make an N x 3 matrix of coordinates
        xyzarr = np.zeros([npart, 3])
        i = 0
        for line in xyzf:
            words = line.split()
            if (len(words) > 3):
                atomnames.append(words[0])
                xyzarr[i][0] = float(words[1])
                xyzarr[i][1] = float(words[2])
                xyzarr[i][2] = float(words[3])
                i = i + 1
    return (xyzarr, atomnames)

def replace_vars(vlist, variables):
    for i in range(len(vlist)):
        if vlist[i] in variables:
            value = variables[vlist[i]]
            vlist[i] = value
        else:
            try:
                value = float(vlist[i])
                vlist[i] = value
            except:
                print "Problem with entry " + str(vlist[i])

def distance_matrix(xyzarr):
    npart, ncoord = xyzarr.shape
    dist_mat = np.zeros([npart, npart])
    for i in range(npart):
        for j in range(0, i):
            rvec = xyzarr[i] - xyzarr[j]
            dist_mat[i][j] = dist_mat[j][i] = np.sqrt(np.dot(rvec, rvec))
    return dist_mat

# --- Distance function --- ###
def getdistance(at1, at2, lol):
	try:
		atom1 = array([float(lol[at1][1]), float(lol[at1][2]), float(lol[at1][3])])
		atom2 = array([float(lol[at2][1]), float(lol[at2][2]), float(lol[at2][3])])
		vector1 = atom2-atom1
		dist = linalg.norm(vector1)
		#print dist
		return dist
	except:
		return 0

def angle(xyzarr, i, j, k): 
    rij = xyzarr[i] - xyzarr[j] 
    rkj = xyzarr[k] - xyzarr[j] 
    cos_theta = np.dot(rij, rkj) 
    sin_theta = np.linalg.norm(np.cross(rij, rkj)) 
    theta = np.arctan2(sin_theta, cos_theta) 
    theta = 180.0 * theta / np.pi 
    return theta 

def dihedral(xyzarr, i, j, k, l): 
    rji = xyzarr[j] - xyzarr[i] 
    rkj = xyzarr[k] - xyzarr[j] 
    rlk = xyzarr[l] - xyzarr[k] 
    v1 = np.cross(rji, rkj) 
    v1 = v1 / np.linalg.norm(v1) 
    v2 = np.cross(rlk, rkj) 
    v2 = v2 / np.linalg.norm(v2) 
    m1 = np.cross(v1, rkj) / np.linalg.norm(rkj) 
    x = np.dot(v1, v2) 
    y = np.dot(m1, v2) 
    chi = np.arctan2(y, x) 
    chi = -180.0 - 180.0 * chi / np.pi 
    if (chi < -180.0): 
        chi = chi + 360.0 
    return chi 

### --- Distance function --- ###
def getdistance(at1, at2, lol):
	try:
		atom1 = array([float(lol[at1][1]), float(lol[at1][2]), float(lol[at1][3])])
		atom2 = array([float(lol[at2][1]), float(lol[at2][2]), float(lol[at2][3])])
		vector1 = atom2-atom1
		dist = linalg.norm(vector1)
		#print dist
		return dist
	except:
		return 0

def output_write(npart, rlist, alist, dlist): 
	file = open("result.txt", "w") 
 
	for i in range(npart-1): 
		file.write('R{:11.5f}\n'.format(i+1, rlist[i])) 
 
	file.write("\n") 
	for i in range(npart-2): 
		file.write('A{:11.5f}\n'.format(i+1, alist[i])) 
 
	file.write("\n") 
	for i in range(npart-3): 
		file.write('D{:11.5f}\n'.format(i+1, dlist[i])) 
 
	file.close() 
	return 

def gen_zmat(xyzarr, distmat, atomnames): 
	npart, ncoord = xyzarr.shape 
    
	rlist = [] 
	alist = [] 
	dlist = [] 
 
	if npart > 1: 
		n = atomnames[1] 
		rlist.append(distmat[0][1]) 
 
		r = '{:>11.5f}'.format(rlist[0]) 
 
		if npart > 2: 
			n = atomnames[2] 
			rlist.append(distmat[0][2]) 
 
			r = '{:>11.5f}'.format(rlist[1]) 
 
			alist.append(angle(xyzarr, 2, 0, 1)) 
			t = '{:>11.5f}'.format(alist[0]) 
 
			if npart > 3: 
				for i in range(3, npart): 
				    n = atomnames[i] 
 
				    rlist.append(distmat[i-3][i]) 
				    r_tmp = '{:>11.5f}'.format(rlist[i-1]) 
 
				    alist.append(angle(xyzarr, i, i-3, i-2)) 
				    a_tmp = '{:>11.5f}'.format(alist[i-2]) 
 
				    dlist.append(dihedral(xyzarr, i, i-3, i-2, i-1)) 
				    d_tmp = '{:>11.5f}'.format(dlist[i-3]) 
 
	return (npart, rlist, alist, dlist) 


rvar = True
xyzfilename = 'data3-1.xyz'

avar = True
xyzarr, atomnames = readxyz(xyzfilename)
distmat = distance_matrix(xyzarr)

dvar = True
    
npart, rlist, alist, dlist = gen_zmat(xyzarr, distmat, atomnames) 
output_write(npart, rlist, alist, dlist) 

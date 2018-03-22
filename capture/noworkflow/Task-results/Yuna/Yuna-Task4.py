import numpy as np
from itertools import islice

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

def readzmat(filename):
    zmatf = open(filename, 'r')
    atomnames = []
    rconnect = []
    rlist = []
    aconnect = []
    alist = []
    dconnect = []
    dlist = []
    variables = {}
    
    if not zmatf.closed:
        lines = list(islice(zmatf, 3))
        for line in lines:
            words = line.split()
            eqwords = line.split('=')
            
            if len(eqwords) > 1:
                varname = str(eqwords[0])
                try:
                    varval  = float(eqwords[1])
                    variables[varname] = varval
                except:
                    print "Invalid variable definition: " + line
            
            else:
                if len(words) > 0:
                    atomnames.append(words[0])
                if len(words) > 1:
                    rconnect.append(int(words[1]))
                if len(words) > 2:
                    rlist.append(words[2])
                if len(words) > 3:
                    aconnect.append(int(words[3]))
                if len(words) > 4:
                    alist.append(words[4])
                if len(words) > 5:
                    dconnect.append(int(words[5]))
                if len(words) > 6:
                    dlist.append(words[6])
    
    replace_vars(rlist, variables)
    replace_vars(alist, variables)
    replace_vars(dlist, variables)
    
    return (atomnames, rconnect, rlist, aconnect, alist, dconnect, dlist) 

def distance_matrix(xyzarr):
    npart, ncoord = xyzarr.shape
    dist_mat = np.zeros([npart, npart])
    for i in range(npart):
        for j in range(0, i):
            rvec = xyzarr[i] - xyzarr[j]
            dist_mat[i][j] = dist_mat[j][i] = np.sqrt(np.dot(rvec, rvec))
    return dist_mat

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
    if (chi  -180.0):
        chi = chi + 360.0
    return chi

def gen_xyz(atomnames, rconnect, rlist, aconnect, alist, dconnect, dlist):
    npart = len(atomnames)

    xyzarr = np.zeros([npart, 3])
    if (npart > 1):
        xyzarr[1] = [rlist[0], 0.0, 0.0]

    if (npart > 2):
        i = rconnect[1] - 1
        j = aconnect[0] - 1
        r = rlist[1]
        theta = alist[0] * np.pi / 180.0
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        a_i = xyzarr[i]
        b_ij = xyzarr[j] - xyzarr[i]
        if (b_ij[0] < 0):
            x = a_i[0] - x
            y = a_i[1] - y
        else:
            x = a_i[0] + x
            y = a_i[1] + y
        xyzarr[2] = [x, y, 0.0]

    for n in range(3, npart):
        r = rlist[n-1]
        theta = alist[n-2] * np.pi / 180.0
        phi = dlist[n-3] * np.pi / 180.0
        
        sinTheta = np.sin(theta)
        cosTheta = np.cos(theta)
        sinPhi = np.sin(phi)
        cosPhi = np.cos(phi)

        x = r * cosTheta
        y = r * cosPhi * sinTheta
        z = r * sinPhi * sinTheta
        
        i = rconnect[n-1] - 1
        j = aconnect[n-2] - 1
        k = dconnect[n-3] - 1
        a = xyzarr[k]
        b = xyzarr[j]
        c = xyzarr[i]
        
        ab = b - a
        bc = c - b
        bc = bc / np.linalg.norm(bc)
        nv = np.cross(ab, bc)
        nv = nv / np.linalg.norm(nv)
        ncbc = np.cross(nv, bc)
        
        new_x = c[0] - bc[0] * x + ncbc[0] * y + nv[0] * z
        new_y = c[1] - bc[1] * x + ncbc[1] * y + nv[1] * z
        new_z = c[2] - bc[2] * x + ncbc[2] * y + nv[2] * z
        new = c[3] - bc[3] * x + ncbc[3] * y + nv[3] * z

        xyzarr[n] = [new_x, new_y, new_z, new]
    return (npart, xyzarr)

def output_write(npart, xyzarr):
    file = open("result.txt", "w")

    for i in range(npart):
        file.write('{:11.5f}\t{:>11.5f}\t{:>11.5f}\n'.format(atomnames[i], xyzarr[i][0], xyzarr[i][1], xyzarr[i][2]))

    file.close()
    return

            
zmatfilename = 'data4-1.zmat'

atomnames, rconnect, rlist, aconnect, alist, dconnect, dlist = readzmat(zmatfilename)
npart, xyzarr = gen_xyz(atomnames, rconnect, rlist, aconnect, alist, dconnect, dlist)
output_write(npart, xyzarr)


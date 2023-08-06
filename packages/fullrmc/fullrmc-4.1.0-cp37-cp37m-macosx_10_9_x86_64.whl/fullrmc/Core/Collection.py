"""
It contains a collection of methods and classes that are useful for the package.
"""
# standard libraries imports
from __future__ import print_function
import os
import sys
import time
import uuid
from random import random  as generate_random_float   # generates a random float number between 0 and 1
from random import randint as generate_random_integer # generates a random integer number between given lower and upper limits

# external libraries imports
import numpy as np
from pdbparser.Utilities.Database import is_element_property, get_element_property

# fullrmc imports
from ..Globals import INT_TYPE, FLOAT_TYPE, PI, PRECISION, LOGGER
from ..Globals import str, long, unicode, bytes, basestring, range, xrange, maxint


def get_caller_frames(engine, frame, subframeToAll, caller):
    """
    Get list of frames for a function caller.

    :Parameters:
        #. engine (None, Engine): The stochastic engine in consideration.
        #. frame (None, string): The frame name. If engine is given as
           None, only None will be accepted as frame value.
        #. subframeToAll (boolean): If frame is a subframe then all multiframe
           subframes must be considered.
        #. caller (string): Caller name for logging and debugging purposes.

    :Returns:
        #. usedIncluded (boolean): Whether engine used frame is included in
           the built frames list. If frame is given as None, True will always
           be returned.
        #. frame (string): The given frame in parameters. If subframe is given
           and subframeToAll is True, then multiframe is returned.
        #. allFrames (list): List of all frames.


    .. code-block:: python

        import inspect
        from fullrmc.Core.Collection import get_caller_frames

        # Assuming self is a constraint and get_caller_frames is called from within a method ...
        usedIncluded, frame, allFrames = get_caller_frames(engine=self.engine,
                                                           frame='frame_name',
                                                           subframeToAll=True,
                                                           caller="%s.%s"%(self.__class__.__name__,inspect.stack()[0][3]) )
    """
    usedFrame = None
    if engine is not None:
        usedFrame = engine.usedFrame
    if frame is None:
        frame        = usedFrame
        usedIncluded = True
        if frame is not None:
            isNormalFrame, isMultiframe, isSubframe = engine.get_frame_category(frame=frame)
            assert not isMultiframe, LOGGER.error("This should have never happened @%s._get_method_frames_from_frame_argument. Please report issue ..."%(caller,))
            if isSubframe and subframeToAll:
                _frame = frame.split(os.sep)[0]
                LOGGER.usage("Given frame is None while engine used frame '%s' is a subframe. %s will be applied to all subframes of '%s'"%(frame, caller, _frame))
                frame     = _frame
                allFrames = [os.path.join(frame, frm) for frm in engine.frames[frame]['frames_name']]
            else:
                allFrames = [frame]
        else:
            allFrames = []
    else:
        assert engine is not None, LOGGER.error("Engine is not given, frame must be None where '%s' is given"%(frame,))
        isNormalFrame, isMultiframe, isSubframe = engine.get_frame_category(frame=frame)
        assert usedFrame is not None, LOGGER.error("This should have never happened @%s._get_method_frames_from_frame_argument. Please report issue ..."%(caller,))
        if isMultiframe or (subframeToAll and isSubframe):
            if isMultiframe:
                LOGGER.usage("Given frame '%s' is a multiframe. %s will be applied to all subframes"%(frame, caller))
            else:
                _frame = frame.split(os.sep)[0]
                LOGGER.usage("Given frame '%s' is a subframe. %s will be applied to all subframes of '%s'"%(frame, caller, _frame))
                frame = _frame
            allFrames = [os.path.join(frame, frm) for frm in engine.frames[frame]['frames_name']]
        else:
            allFrames = [frame]
        usedIncluded = usedFrame==frame or usedFrame.split(os.sep)[0] == frame
    # return
    return usedIncluded, frame, allFrames


def get_real_elements_weight(elements, weightsDict, weighting):
    """
    Get elements weights given a dictionary of weights and a weighting scheme.
    If element weight is not defined in weightsDict then weight is fetched
    from pdbparser elements database using weighting scheme.

    :Parameters:
        #. elements (list): List of elements.
        #. weightsDict (dict): Dictionary of fixed weights.
        #. weighting (str): Weighting scheme.

    :Returns:
        #. elementsWeight (dict): Elements weights got from weightsDict
           and completed using weighting scheme,
    """
    elementsWeight = {}
    for el in elements:
        w = weightsDict.get(el, get_element_property(el,weighting))
        if w is None:
            raise LOGGER.error("element '%s' weight is found to be None. Numerical elements weight is required."%(el) )
        if isinstance(w, complex):
            LOGGER.fixed("element '%s' weight is found to be complex '%s'. Value is cast to its real part."%(el,w) )
            w = w.real
        try:
            w = FLOAT_TYPE(w)
        except:
            raise LOGGER.error("element '%s' is found to not numerical '%s'."%(el,w) )
        elementsWeight[el] = w
    # return dict
    return elementsWeight

def raise_if_collected(func):
    """ Constraints method decorator that raises an error whenever the
    method is called and the system has atoms that were removed.
    """
    def wrapper(self, *args, **kwargs):
        assert not len(self._atomsCollector), LOGGER.error("Calling '%s.%s' is not allowed when system has collected atoms."%(self.__class__.__name__,func.__name__))
        return func(self, *args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__  = func.__doc__
    return wrapper

def reset_if_collected_out_of_date(func):
    """ Constraints method decorator that resets the constraint whenever
    the method is called and the system has atoms that were removed.
    """
    def wrapper(self, *args, **kwargs):
        if self.engine is not None:
            if set(self.engine._atomsCollector.indexes) != set(self._atomsCollector.indexes):
                # reset constraints
                self.reset_constraint()
                # collect atoms
                for realIndex in self.engine._atomsCollector.indexes:
                    self._on_collector_collect_atom(realIndex=realIndex)
        return func(self, *args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__  = func.__doc__
    return wrapper

def is_number(number):
    """
    Check if number is convertible to float.

    :Parameters:
        #. number (str, number): Input number.

    :Returns:
        #. result (bool): True if convertible, False otherwise
    """
    if isinstance(number, (int, long, float, complex)):
        return True
    try:
        float(number)
    except:
        return False
    else:
        return True

def is_integer(number, precision=10e-10):
    """
    Check if number is convertible to integer.

    :Parameters:
        #. number (str, number): Input number.
        #. precision (number): To avoid floating errors,
           a precision should be given.

    :Returns:
        #. result (bool): True if convertible, False otherwise.
    """
    if isinstance(number, (int, long)):
        return True
    try:
        number = float(number)
    except:
        return False
    else:
        if np.abs(number-int(number)) < precision:
            return True
        else:
            return False

def get_elapsed_time(start, format="%d days, %d hours, %d minutes, %d seconds"):
    """
    Get formatted time elapsed.

    :Parameters:
        #. start (time.time): A time instance.
        #. format (string): The format string. must contain exactly four '%d'.

    :Returns:
        #. time (string): The formatted elapsed time.
    """
    # get all time info
    days    = divmod(time.time()-start,86400)
    hours   = divmod(days[1],3600)
    minutes = divmod(hours[1],60)
    seconds = minutes[1]
    return format % (days[0],hours[0],minutes[0],seconds)


def get_memory_usage():
    """
    Get current process memory usage. This is method requires
    psutils to be installed.

    :Returns:
        #. memory (float, None): The memory usage in Megabytes.
           When psutils is not installed, None is returned.
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory  = float( process.memory_info()[0] ) / float(2 ** 20)
    except:
        LOGGER.warn("memory usage cannot be profiled. psutil is not installed. pip install psutil")
        memory = None
    return memory


def get_path(key=None):
    """
    Get all paths information needed about the running script and python
    executable path.

    :Parameters:
        #. key (None, string): the path to return. If not None is given,
        it can take any of the following:\n
            #. cwd:                 current working directory
            #. script:              the script's total path
            #. exe:                 python executable path
            #. script_name:         the script name
            #. relative_script_dir: the script's relative directory path
            #. script_dir:          the script's absolute directory path
            #. fullrmc:             fullrmc package path

    :Returns:
        #. path (dictionary, value): If key is not None it returns the value of paths
           dictionary key. Otherwise all the dictionary is returned.
    """
    import fullrmc
    # check key type
    if key is not None:
        assert isinstance(key, basestring), LOGGER.error("key must be a string of None")
        key=str(key).lower().strip()
    # create paths
    paths = {}
    paths["cwd"]                 = os.getcwd()
    paths["script"]              = sys.argv[0]
    paths["exe"]                 = os.path.dirname(sys.executable)
    pathname, scriptName         = os.path.split(sys.argv[0])
    paths["script_name"]         = scriptName
    paths["relative_script_dir"] = pathname
    paths["script_dir"]          = os.path.abspath(pathname)
    paths["fullrmc"]             = os.path.split(fullrmc.__file__)[0]
    # return paths
    if key is None:
        return paths
    else:
        assert key in paths, LOGGER.error("key is not defined")
        return paths[key]


def rebin(data, bin=0.05, check=False):
    """
    Re-bin 2D data of shape (N,2). In general, fullrmc requires equivalently
    spaced experimental data bins. This function can be used to recompute
    any type of experimental data according to a set bin size.

    :Parameters:
        #. data (numpy.ndarray): The (N,2) shape data where first column is
           considered experimental data space values (e.g. r, q) and
           second column experimental data values.
        #. bin (number): New desired bin size.
        #. check (boolean): whether to check arguments before rebining.

    :Returns:
        #. X (numpy.ndarray): First column re-binned.
        #. Y (numpy.ndarray): Second column re-binned.
    """
    if check:
        assert isinstance(data, np.ndarray), Logger.error("data must be numpy.ndarray instance")
        assert len(data.shape)==2, Logger.error("data must be of 2 dimensions")
        assert data.shape[1] ==2, Logger.error("data must have 2 columns")
        assert is_number(bin), LOGGER.error("bin must be a number")
        bin = float(bin)
        assert bin>0, LOGGER.error("bin must be a positive")
    # rebin
    x = data[:,0].astype(float)
    y = data[:,1].astype(float)
    rx = []
    ry = []
    x0 = int(x[0]/bin)*bin-bin/2.
    xn = int(x[-1]/bin)*bin+bin/2.
    bins = np.arange(x0,xn, bin)
    if bins[-1] != xn:
        bins = np.append(bins, xn)
    # get weights histogram
    W,E = np.histogram(x, bins=bins)
    W[np.where(W==0)[0]] = 1
    # get data histogram
    S,E = np.histogram(x, bins=bins, weights=y)
    # return
    return (E[1:]+E[:-1])/2., S/W

def smooth(data, winLen=11, window='hanning', check=False):
    """
    Smooth 1D data using window function and length.

    :Parameters:
        #. data (numpy.ndarray): the 1D numpy data.
        #. winLen (integer): the smoothing window length.
        #. window (str): The smoothing window type. Can be anything among
           'flat', 'hanning', 'hamming', 'bartlett' and 'blackman'.
        #. check (boolean): whether to check arguments before smoothing data.

    :Returns:
        #. smoothed (numpy.ndarray): the smoothed 1D data array.
    """
    if check:
        assert isinstance(data, np.ndarray), Logger.error("data must be numpy.ndarray instance")
        assert len(data.shape)==1, Logger.error("data must be of 1 dimensions")
        assert is_integer(winLen), LOGGER.error("winLen must be an integer")
        winLen = int(bin)
        assert winLen>=3, LOGGER.error("winLen must be bigger than 3")
        assert data.size < winLen, LOGGER.error("data needs to be bigger than window size.")
        assert window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman'], LOGGER.error("window must be any of ('flat', 'hanning', 'hamming', 'bartlett', 'blackman')")
    # compute smoothed data
    s=np.r_[data[winLen-1:0:-1],data,data[-1:-winLen:-1]]
    if window == 'flat': #moving average
        w=np.ones(winLen,'d')
    else:
        w=eval('np.'+window+'(winLen)')
    S=np.convolve(w/w.sum(),s, mode='valid')
    # get data and return
    f = winLen/2
    t = f-winLen+1
    return S[f:t]

def get_random_perpendicular_vector(vector):
    """
    Get random normalized perpendicular vector to a given vector.

    :Parameters:
        #. vector (numpy.ndarray, list, set, tuple): Given vector to compute
           a random perpendicular vector to it.

    :Returns:
        #. perpVector (numpy.ndarray): Perpendicular vector of type
           fullrmc.Globals.FLOAT_TYPE
    """
    vectorNorm = np.linalg.norm(vector)
    assert vectorNorm, LOGGER.error("vector returned 0 norm")
    # easy cases
    if np.abs(vector[0])<PRECISION:
        return np.array([1,0,0], dtype=FLOAT_TYPE)
    elif np.abs(vector[1])<PRECISION:
        return np.array([0,1,0], dtype=FLOAT_TYPE)
    elif np.abs(vector[2])<PRECISION:
        return np.array([0,0,1], dtype=FLOAT_TYPE)
    # generate random vector
    randVect = 1-2*np.random.random(3)
    randvect = np.array([vector[idx]*randVect[idx] for idx in range(3)])
    # get perpendicular vector
    perpVector = np.cross(randvect,vector)
    # normalize, coerce and return
    return np.array(perpVector/np.linalg.norm(perpVector), dtype=FLOAT_TYPE)


def get_principal_axis(coordinates, weights=None):
    """
    Calculate principal axis of a set of atoms coordinates.

    :Parameters:
        #. coordinates (np.ndarray): Atoms (N,3) coordinates array.
        #. weights (numpy.ndarray, None): List of weights to compute the
           weighted Center Of Mass (COM) calculation. Must be a numpy.ndarray
           of numbers of the same length as indexes. None is accepted for
           equivalent weighting.

    :Returns:
        #. center (numpy.ndarray): the weighted COM of the atoms.
        #. eval1 (fullrmc.Globals.FLOAT_TYPE): Biggest eigen value.
        #. eval2 (fullrmc.Globals.FLOAT_TYPE): Second biggest eigen value.
        #. eval3 (fullrmc.Globals.FLOAT_TYPE): Smallest eigen value.
        #. axis1 (numpy.ndarray): Principal axis corresponding to the
           biggest eigen value.
        #. axis2 (numpy.ndarray): Principal axis corresponding to the
           second biggest eigen value.
        #. axis3 (numpy.ndarray): Principal axis corresponding to the
           smallest eigen value.
    """
    # multiply by weights
    if weights is not None:
        coordinates[:,0] *= weights
        coordinates[:,1] *= weights
        coordinates[:,2] *= weights
        norm = np.sum(weights)
    else:
        norm = coordinates.shape[0]
    # compute center
    center = np.array(np.sum(coordinates, 0)/norm, dtype=FLOAT_TYPE)
    # coordinates in center
    centerCoords = coordinates - center
    # compute principal axis matrix
    inertia = np.dot(centerCoords.transpose(), centerCoords)
    # compute eigen values and eigen vectors
    # warning eigen values are not necessary ordered!
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.eig.html
    e_values, e_vectors = np.linalg.eig(inertia)
    e_values  = list(e_values)
    e_vectors = list(e_vectors.transpose())
    # get eval1 and axis1
    eval1 = max(e_values)
    vect1 = np.array(e_vectors.pop(e_values.index(eval1)), dtype=FLOAT_TYPE)
    e_values.remove(eval1)
    # get eval1 and axis1
    eval2 = max(e_values)
    vect2 = np.array(e_vectors.pop(e_values.index(eval2)), dtype=FLOAT_TYPE)
    e_values.remove(eval2)
    # get eval3 and axis3
    eval3 = e_values[0]
    vect3 = np.array(e_vectors[0], dtype=FLOAT_TYPE)
    return center, FLOAT_TYPE(eval1), FLOAT_TYPE(eval2), FLOAT_TYPE(eval3), vect1, vect2, vect3


def get_rotation_matrix(rotationVector, angle):
    """
    Calculate the rotation (3X3) matrix about an axis (rotationVector)
    by a rotation angle.

    :Parameters:
        #. rotationVector (list, tuple, numpy.ndarray): Rotation axis
           coordinates.
        #. angle (float): Rotation angle in rad.

    :Returns:
        #. rotationMatrix (numpy.ndarray): Computed (3X3) rotation matrix
    """
    angle = float(angle)
    axis = rotationVector/np.sqrt(np.dot(rotationVector , rotationVector))
    a = np.cos(angle/2)
    b,c,d = -axis*np.sin(angle/2.)
    return np.array( [ [a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                       [2*(b*c+a*d), a*a+c*c-b*b-d*d, 2*(c*d-a*b)],
                       [2*(b*d-a*c), 2*(c*d+a*b), a*a+d*d-b*b-c*c] ] , dtype = FLOAT_TYPE)

def rotate(xyzArray , rotationMatrix):
    """
    Rotate (N,3) numpy.array using a rotation matrix.
    The array itself will be rotated and not a copy of it.

    :Parameters:
        #. indexes (numpy.ndarray): the xyz (N,3) array to rotate.
        #. rotationMatrix (numpy.ndarray): the (3X3) rotation matrix.
    """
    arrayType = xyzArray.dtype
    for idx in range(xyzArray.shape[0]):
        xyzArray[idx,:] = np.dot( rotationMatrix, xyzArray[idx,:]).astype(arrayType)
    return xyzArray

def get_orientation_matrix(arrayAxis, alignToAxis):
    """
    Get the rotation matrix that aligns arrayAxis to alignToAxis

    :Parameters:
        #. arrayAxis (list, tuple, numpy.ndarray): xyzArray axis.
        #. alignToAxis (list, tuple, numpy.ndarray): The axis to align to.
    """
    # normalize alignToAxis
    alignToAxisNorm = np.linalg.norm(alignToAxis)
    assert alignToAxisNorm>0, LOGGER.error("alignToAxis returned 0 norm")
    alignToAxis = np.array(alignToAxis, dtype=FLOAT_TYPE)/alignToAxisNorm
    # normalize arrayAxis
    arrayAxisNorm = np.linalg.norm(arrayAxis)
    assert arrayAxisNorm>0, LOGGER.error("arrayAxis returned 0 norm")
    arrayAxis = np.array(arrayAxis, dtype=FLOAT_TYPE)/arrayAxisNorm
    # calculate rotationAngle
    dotProduct = np.dot(arrayAxis, alignToAxis)
    if np.abs(dotProduct-1) <= PRECISION :
        rotationAngle = 0
    elif np.abs(dotProduct+1) <= PRECISION :
        rotationAngle = PI
    else:
        rotationAngle = np.arccos( dotProduct )
    if np.isnan(rotationAngle) or np.abs(rotationAngle) <= PRECISION :
        return np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]).astype(FLOAT_TYPE)
    # calculate rotation axis.
    if np.abs(rotationAngle-PI) <= PRECISION:
        rotationAxis = get_random_perpendicular_vector(arrayAxis)
    else:
        rotationAxis = np.cross(alignToAxis, arrayAxis)
    #rotationAxis /= np.linalg.norm(rotationAxis)
    # calculate rotation matrix
    return get_rotation_matrix(rotationAxis, rotationAngle)


def orient(xyzArray, arrayAxis, alignToAxis):
    """
    Rotates xyzArray using the rotation matrix that rotates and aligns
    arrayAxis to alignToAXis.

    :Parameters:
        #. xyzArray (numpy.ndarray): The xyz (N,3) array to rotate.
        #. arrayAxis (list, tuple, numpy.ndarray): xyzArray axis.
        #. alignToAxis (list, tuple, numpy.ndarray): The axis to align to.
    """
    # normalize alignToAxis
    alignToAxisNorm = np.linalg.norm(alignToAxis)
    assert alignToAxisNorm>0, LOGGER.error("alignToAxis returned 0 norm")
    alignToAxis = np.array(alignToAxis, dtype=FLOAT_TYPE)/alignToAxisNorm
    # normalize arrayAxis
    arrayAxisNorm = np.linalg.norm(arrayAxis)
    assert arrayAxisNorm>0, LOGGER.error("arrayAxis returned 0 norm")
    arrayAxis = np.array(arrayAxis, dtype=FLOAT_TYPE)/arrayAxisNorm
    # calculate rotationAngle
    dotProduct = np.dot(arrayAxis, alignToAxis)
    if np.abs(dotProduct-1) <= PRECISION :
        rotationAngle = 0
    elif np.abs(dotProduct+1) <= PRECISION :
        rotationAngle = PI
    else:
        rotationAngle = np.arccos( dotProduct )
    if np.isnan(rotationAngle) or np.abs(rotationAngle) <= PRECISION :
        return xyzArray
    # calculate rotation axis.
    if np.abs(rotationAngle-PI) <= PRECISION:
        rotationAxis = get_random_perpendicular_vector(arrayAxis)
    else:
        rotationAxis = np.cross(alignToAxis, arrayAxis)
    #rotationAxis /= np.linalg.norm(rotationAxis)
    # calculate rotation matrix
    rotationMatrix = get_rotation_matrix(rotationAxis, rotationAngle)
    # rotate and return
    return rotate(xyzArray , rotationMatrix)



def get_superposition_transformation(refArray, array, check=False):
    """
    Calculate the rotation tensor and the translations that minimizes
    the root mean square deviation between an array of vectors
    and a reference array.

    :Parameters:
        #. refArray (numpy.ndarray): The NX3 reference array to
           superpose to.
        #. array (numpy.ndarray): The NX3 array to calculate the
           transformation of.
        #. check (boolean): Whether to check arguments before
           generating points.

    :Returns:
        #. rotationMatrix (numpy.ndarray): The 3X3 rotation tensor.
        #. refArrayCOM (numpy.ndarray): The 1X3 vector center of mass of
           refArray.
        #. arrayCOM (numpy.ndarray): The 1X3 vector center of mass of array.
        #. rms (number)
    """
    if check:
        # check array
        assert isinstance(array, np.ndarray), Logger.error("array must be numpy.ndarray instance")
        assert len(array.shape)<=2, Logger.error("array must be a vector or a matrix")
        if len(array.shape)==2:
            assert array.shape[1]==3, Logger.error("array number of columns must be 3")
        else:
            assert array.shape[1]==3, Logger.error("vector array number of columns must be 3")
        # check refArray
        assert isinstance(refArray, np.ndarray), Logger.error("refArray must be numpy.ndarray instance")
        assert len(refArray.shape)<=2, Logger.error("refArray must be a vector or a matrix")
        if len(refArray.shape)==2:
            assert refArray.shape[1]==3, Logger.error("refArray number of columns must be 3")
        else:
            assert refArray.shape[1]==3, Logger.error("vector refArray number of columns must be 3")
        # check weights
        assert array.shape == refArray.shape, Logger.error("refArray and array must have the same number of vectors")
    # calculate center of mass of array
    arrayCOM = np.sum(array, axis=0)/array.shape[0]
    # calculate cross matrix and reference config center of mass
    r_ref = array-arrayCOM
    refArrayCOM = np.sum(refArray, axis=1)
    cross = np.dot(refArray.transpose(),r_ref)
    possq = np.add.reduce(refArray**2,1)+np.add.reduce(r_ref**2,1)
    possq = np.sum(possq)
    # calculate kross
    kross = np.zeros((4, 4), dtype=FLOAT_TYPE)
    kross[0, 0] = -cross[0, 0]-cross[1, 1]-cross[2, 2]
    kross[0, 1] =  cross[1, 2]-cross[2, 1]
    kross[0, 2] =  cross[2, 0]-cross[0, 2]
    kross[0, 3] =  cross[0, 1]-cross[1, 0]
    kross[1, 1] = -cross[0, 0]+cross[1, 1]+cross[2, 2]
    kross[1, 2] = -cross[0, 1]-cross[1, 0]
    kross[1, 3] = -cross[0, 2]-cross[2, 0]
    kross[2, 2] =  cross[0, 0]-cross[1, 1]+cross[2, 2]
    kross[2, 3] = -cross[1, 2]-cross[2, 1]
    kross[3, 3] =  cross[0, 0]+cross[1, 1]-cross[2, 2]
    for i in range(1, 4):
        for j in range(i):
            kross[i, j] = kross[j, i]
    kross = 2.*kross
    offset = possq - np.add.reduce(refArrayCOM**2)
    for i in range(4):
        kross[i, i] = kross[i, i] + offset
    # get eigen values
    e, v = np.linalg.eig(kross)
    i = np.argmin(e)
    v = np.array(v[:,i], dtype=FLOAT_TYPE)
    if v[0] < 0: v = -v
    if e[i] <= 0.:
        rms = FLOAT_TYPE(0.)
    else:
        rms = np.sqrt(e[i])
    # calculate the rotation matrix
    rot = np.zeros((3,3,4,4), dtype=FLOAT_TYPE)
    rot[0,0, 0,0] = FLOAT_TYPE( 1.0)
    rot[0,0, 1,1] = FLOAT_TYPE( 1.0)
    rot[0,0, 2,2] = FLOAT_TYPE(-1.0)
    rot[0,0, 3,3] = FLOAT_TYPE(-1.0)
    rot[1,1, 0,0] = FLOAT_TYPE( 1.0)
    rot[1,1, 1,1] = FLOAT_TYPE(-1.0)
    rot[1,1, 2,2] = FLOAT_TYPE( 1.0)
    rot[1,1, 3,3] = FLOAT_TYPE(-1.0)
    rot[2,2, 0,0] = FLOAT_TYPE( 1.0)
    rot[2,2, 1,1] = FLOAT_TYPE(-1.0)
    rot[2,2, 2,2] = FLOAT_TYPE(-1.0)
    rot[2,2, 3,3] = FLOAT_TYPE( 1.0)
    rot[0,1, 1,2] = FLOAT_TYPE( 2.0)
    rot[0,1, 0,3] = FLOAT_TYPE(-2.0)
    rot[0,2, 0,2] = FLOAT_TYPE( 2.0)
    rot[0,2, 1,3] = FLOAT_TYPE( 2.0)
    rot[1,0, 0,3] = FLOAT_TYPE( 2.0)
    rot[1,0, 1,2] = FLOAT_TYPE( 2.0)
    rot[1,2, 0,1] = FLOAT_TYPE(-2.0)
    rot[1,2, 2,3] = FLOAT_TYPE( 2.0)
    rot[2,0, 0,2] = FLOAT_TYPE(-2.0)
    rot[2,0, 1,3] = FLOAT_TYPE( 2.0)
    rot[2,1, 0,1] = FLOAT_TYPE( 2.0)
    rot[2,1, 2,3] = FLOAT_TYPE( 2.0)
    rotationMatrix = np.dot(np.dot(rot, v), v)
    return rotationMatrix, refArrayCOM, arrayCOM, rms


def superpose_array(refArray, array, check=False):
    """
    Superpose arrays by calculating the rotation matrix and the
    translations that minimize the root mean square deviation between and
    array of vectors and a reference array.

    :Parameters:
        #. refArray (numpy.ndarray): the NX3 reference array to superpose to.
        #. array (numpy.ndarray): the NX3 array to calculate the
           transformation of.
        #. check (boolean): whether to check arguments before generating
           points.

    :Returns:
        #. superposedArray (numpy.ndarray): the NX3 array to superposed array.
    """
    rotationMatrix, _,_,_ = get_superposition_transformation(refArray=refArray, array=array, check=check)
    return np.dot( rotationMatrix, np.transpose(array).\
                   reshape(1,3,-1)).transpose().reshape(-1,3)


def generate_random_vector(minAmp, maxAmp):
    """
    Generate random vector in 3D.

    :Parameters:
        #. minAmp (number): Vector minimum amplitude.
        #. maxAmp (number): Vector maximum amplitude.

    :Returns:
        #. vector (numpy.ndarray): the vector [X,Y,Z] array
    """
    # generate random vector and ensure it is not zero
    vector = np.array(1-2*np.random.random(3), dtype=FLOAT_TYPE)
    norm   = np.linalg.norm(vector)
    if norm == 0:
        while norm == 0:
            vector = np.array(1-2*np.random.random(3), dtype=FLOAT_TYPE)
            norm   = np.linalg.norm(vector)
    # normalize vector
    vector /= FLOAT_TYPE( norm )
    # compute baseVector
    baseVector = FLOAT_TYPE(vector*minAmp)
    # amplify vector
    maxAmp  = FLOAT_TYPE(maxAmp-minAmp)
    vector *= FLOAT_TYPE(generate_random_float()*maxAmp)
    vector += baseVector
    # return vector
    return vector


def generate_points_on_sphere(thetaFrom, thetaTo,
                              phiFrom, phiTo,
                              npoints=1,
                              check=False):
    """
    Generate random points on a sphere of radius 1. Points are generated
    using spherical coordinates arguments as in figure below. Theta [0,Pi]
    is the angle between the generated point and Z axis. Phi [0,2Pi] is the
    angle between the generated point and x axis.

    .. image:: sphericalCoordsSystem.png
       :align: left
       :height: 200px
       :width: 200px

    :Parameters:
        #. thetaFrom (number): The minimum theta value.
        #. thetaTo (number): The maximum theta value.
        #. phiFrom (number): The minimum phi value.
        #. phiTo (number): The maximum phi value.
        #. npoints (integer): The number of points to generate
        #. check (boolean): whether to check arguments before generating points.

    :Returns:
        #. x (numpy.ndarray): The (npoints,1) numpy array of all generated
           points x coordinates.
        #. y (numpy.ndarray): The (npoints,1) numpy array of all generated
           points y coordinates.
        #. z (numpy.ndarray): The (npoints,1) numpy array of all generated
           points z coordinates.
    """
    if check:
        assert isinteger(npoints)   , LOGGER.error("npoints must be an integer")
        assert is_number(thetaFrom) , LOGGER.error("thetaFrom must be a number")
        assert is_number(thetaTo)   , LOGGER.error("thetaTo must be a number")
        assert is_number(phiFrom)   , LOGGER.error("phiFrom must be a number")
        assert is_number(phiTo)     , LOGGER.error("phiTo must be a number")
        npoints   = INT_TYPE(npoints)
        thetaFrom = FLOAT_TYPE(thetaFrom)
        thetaTo   = FLOAT_TYPE(thetaTo)
        phiFrom   = FLOAT_TYPE(phiFrom)
        phiTo     = FLOAT_TYPE(phiTo)
        assert npoints>=1        , LOGGER.error("npoints must be bigger than 0")
        assert thetaFrom>=0      , LOGGER.error("thetaFrom must be positive")
        assert thetaTo<=PI       , LOGGER.error("thetaTo must be smaller than %.6f"%PI)
        assert thetaFrom<thetaTo , LOGGER.error("thetaFrom must be smaller than thetaTo")
        assert phiFrom>=0        , LOGGER.error("phiFrom must be positive")
        assert phiTo<=2*PI       , LOGGER.error("phiTo mast be smaller than %.6f"%2*PI)
        assert phiFrom<phiTo     , LOGGER.error("phiFrom must be smaller than phiTo")
    else:
        # cast variables
        npoints   = INT_TYPE(npoints)
        thetaFrom = FLOAT_TYPE(thetaFrom)
        thetaTo   = FLOAT_TYPE(thetaTo)
        phiFrom   = FLOAT_TYPE(phiFrom)
        phiTo     = FLOAT_TYPE(phiTo)
    # calculate differences
    deltaTheta = thetaTo-thetaFrom
    deltaPhi = phiTo-phiFrom
    # theta
    theta  = thetaFrom+np.random.random(npoints).astype(FLOAT_TYPE)*deltaTheta
    # phi
    phi  = phiFrom+np.random.random(npoints).astype(FLOAT_TYPE)*deltaPhi
    # compute sin and cos
    sinTheta = np.sin(theta)
    sinPhi   = np.sin(phi)
    cosTheta = np.cos(theta)
    cosPhi   = np.cos(phi)
    # compute x,y,z
    x = sinTheta * cosPhi
    y = sinTheta * sinPhi
    z = cosTheta
    # return
    return x,y,z


def find_extrema(x, max = True, min = True, strict = False, withend = False):
    """
    Get a vector extrema indexes and values.

    :Parameters:
        #. max (boolean): Whether to index the maxima.
        #. min (boolean): Whether to index the minima.
        #. strict (boolean): Whether not to index changes to zero gradient.
        #. withend (boolean): Whether to always include x[0] and x[-1].

    :Returns:
        #. indexes (numpy.ndarray): Extrema indexes.
        #. values (numpy.ndarray): Extrema values.
    """
    # This is the gradient
    dx = np.empty(len(x))
    dx[1:] = np.diff(x)
    dx[0] = dx[1]
    # Clean up the gradient in order to pick out any change of sign
    dx = np.sign(dx)
    # define the threshold for whether to pick out changes to zero gradient
    threshold = 0
    if strict:
        threshold = 1
    # Second order diff to pick out the spikes
    d2x = np.diff(dx)
    if max and min:
        d2x = abs(d2x)
    elif max:
        d2x = -d2x
    # Take care of the two ends
    if withend:
        d2x[0] = 2
        d2x[-1] = 2
    # Sift out the list of extremas
    ind = np.nonzero(d2x > threshold)[0]
    return ind, x[ind]


def convert_Gr_to_gr(Gr, minIndex):
    """
    Converts G(r) to g(r) by computing the following
    :math:`g(r)=1+(\\frac{G(r)}{4 \\pi \\rho_{0} r})`

    :Parameters:
        #. Gr (numpy.ndarray): The G(r) numpy array of shape
           (number of points, 2)
        #. minIndex (int, tuple): The minima indexes to compute the
           number density rho0. It can be a single peak or a list of peaks to
           compute the mean slope instead.

    :Returns:
        #. minimas (numpy.ndarray): The minimas array found using minIndex
           and used to compute the slope and therefore :math:`\\rho_{0}`.
        #. slope (float): The computed slope from the minimas.
        #. rho0 (float): The number density of the material.
        #. g(r) (numpy.ndarray): the computed g(r).


    **To visualize convertion**

    .. code-block:: python

        # peak indexes can be different, adjust according to your data
        minPeaksIndex = [1,3,4]
        minimas, slope, rho0, gr =  convert_Gr_to_gr(Gr, minIndex=minPeaksIndex)
        print('slope: %s --> rho0: %s'%(slope,rho0))
        import matplotlib.pyplot as plt
        line = np.transpose( [[0, Gr[-1,0]], [0, slope*Gr[-1,0]]] )
        plt.plot(Gr[:,0],Gr[:,1], label='G(r)')
        plt.plot(minimas[:,0], minimas[:,1], 'o', label='minimas')
        plt.plot(line[:,0], line[:,1], label='density')
        plt.plot(gr[:,0],gr[:,1], label='g(r)')
        plt.legend()
        plt.show()

    """
    # check G(r)
    assert isinstance(Gr, np.ndarray), "Gr must be a numpy.ndarray"
    assert len(Gr.shape)==2, "Gr be of shape length 2"
    assert Gr.shape[1] == 2, "Gr must be of shape (n,2)"
    # check minIndex
    if not isinstance(minIndex, (list, set, tuple)):
        minIndex = [minIndex]
    else:
        minIndex = list(minIndex)
    for idx, mi in enumerate(minIndex):
        assert is_integer(mi), "minIndex must be integers"
        mi = int(mi)
        assert mi>=0, "minIndex must be >0"
        minIndex[idx] = mi
    # get minsIndexes
    minsIndexes = find_extrema(x=Gr[:,1], max=False)[0]
    # get minimas points
    minIndex = [minsIndexes[mi] for mi in minIndex]
    minimas  = np.transpose([Gr[minIndex,0], Gr[minIndex,1]])
    # compute slope
    x = float( np.mean(minimas[:,0]) )
    y = float( np.mean(minimas[:,1]) )
    slope = y/x
    # compute rho
    rho0 = -slope/4./np.pi
    # compute g(r)
    gr = 1+Gr[:,1]/(-slope*Gr[:,0])
    gr = np.transpose( [Gr[:,0], gr] )
    # return
    return minimas, slope, rho0, gr


def generate_vectors_in_solid_angle(direction,
                                    maxAngle,
                                    numberOfVectors=1,
                                    check=False):
    """
    Generate random vectors that satisfy angle condition with a
    direction vector. Angle between any generated vector and direction must
    be smaller than given maxAngle.

    +----------------------------------------+----------------------------------------+----------------------------------------+
    |.. figure:: 100randomVectors30deg.png   |.. figure:: 200randomVectors45deg.png   |.. figure:: 500randomVectors100deg.png  |
    |   :width: 400px                        |   :width: 400px                        |   :width: 400px                        |
    |   :height: 300px                       |   :height: 300px                       |   :height: 300px                       |
    |   :align: left                         |   :align: left                         |   :align: left                         |
    |                                        |                                        |                                        |
    |   a) 100 vectors generated around      |   b) 200 vectors generated around      |   b) 500 vectors generated around      |
    |   OX axis within a maximum angle       |   [1,-1,1] axis within a maximum angle |   [2,5,1] axis within a maximum angle  |
    |   separation of 30 degrees.            |   separation of 45 degrees.            |   separation of 100 degrees.           |
    +----------------------------------------+----------------------------------------+----------------------------------------+

    :Parameters:
        #. direction (number): The direction around which to create the vectors.
        #. maxAngle (number): The maximum angle allowed.
        #. numberOfVectors (integer): The number of vectors to generate.
        #. check (boolean): whether to check arguments before generating
           vectors.

    :Returns:
        #. vectors (numpy.ndarray): The (numberOfVectors,3) numpy array of
           generated vectors.
    """
    if check:
        assert isinstance(direction, (list,set,tuple,np.array)), LOGGER.error("direction must be a vector like list or array of length 3")
        direction = list(direction)
        assert len(direction)==3, LOGGER.error("direction vector must be of length 3")
        dir = []
        for d in direction:
            assert is_number(d), LOGGER.error("direction items must be numbers")
            dir.append(FLOAT_TYPE(d))
        direction = np.array(dir)
        assert direction[0]>PRECISION or direction[1]>PRECISION or direction[2]>PRECISION, LOGGER.error("direction must be a non zero vector")
        assert is_number(maxAngle), LOGGER.error("maxAngle must be a number")
        maxAngle = FLOAT_TYPE(maxAngle)
        assert maxAngle>0, LOGGER.error("maxAngle must be bigger that zero")
        assert maxAngle<=PI, LOGGER.error("maxAngle must be smaller than %.6f"%PI)
        assert is_integer(numberOfVectors), LOGGER.error("numberOfVectors must be integer")
        numberOfVectors = INT_TYPE(numberOfVectors)
        assert numberOfVectors>0, LOGGER.error("numberOfVectors must be bigger than 0")
    # create axis
    axis = np.array([1,0,0])
    if np.abs(direction[1])<=PRECISION and np.abs(direction[2])<=PRECISION:
        axis *= np.sign(direction[0])
    # create vectors
    vectors = np.zeros((numberOfVectors,3))
    vectors[:,1] = 1-2*np.random.random(numberOfVectors)
    vectors[:,2] = 1-2*np.random.random(numberOfVectors)#np.sign(np.random.random(numberOfVectors)-0.5)*np.sqrt(1-vectors[:,1]**2)
    norm = np.sqrt(np.add.reduce(vectors**2, axis=1))
    vectors[:,1] /= norm
    vectors[:,2] /= norm
    # create rotation angles
    rotationAngles = PI/2.-np.random.random(numberOfVectors)*maxAngle
    # create rotation axis
    rotationAxes = np.cross(axis, vectors)
    # rotate vectors to axis
    for idx in range(numberOfVectors):
        rotationMatrix = get_rotation_matrix(rotationAxes[idx,:], rotationAngles[idx])
        vectors[idx,:] = np.dot( rotationMatrix, vectors[idx,:])
    # normalize direction
    direction /= np.linalg.norm(direction)
    # get rotation matrix of axis to direction
    rotationAngle  = np.arccos( np.dot(direction, axis) )
    if rotationAngle > PRECISION:
        rotationAxis   = np.cross(direction, axis)
        rotationMatrix = get_rotation_matrix(rotationAxis, rotationAngle)
        # rotate vectors to direction
        for idx in range(numberOfVectors):
            vectors[idx,:] = np.dot( rotationMatrix, vectors[idx,:])
    return vectors.astype(FLOAT_TYPE)


def gaussian(x, center=0, FWHM=1, normalize=True, check=True):
    """
    Compute the normal distribution or gaussian distribution of a given vector.
    The probability density of the gaussian distribution is:
    :math:`f(x,\\mu,\\sigma) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{\\frac{-(x-\\mu)^{2}}{2\\sigma^2}}`

    Where:\n
    * :math:`\\mu` is the center of the gaussian, it is the mean or
      expectation of the distribution it is called the distribution's
      median or mode.
    * :math:`\\sigma` is its standard deviation.
    * :math:`FWHM=2\\sqrt{2 ln 2} \\sigma` is the Full Width at Half
      Maximum of the gaussian.

    :Parameters:
        #. x (numpy.ndarray): The vector to compute the gaussian
        #. center (number): The center of the gaussian.
        #. FWHM (number): The Full Width at Half Maximum of the gaussian.
        #. normalize(boolean): Whether to normalize the generated gaussian
           by :math:`\\frac{1}{\\sigma\\sqrt{2\\pi}}` so the integral
           is equal to 1.
        #. check (boolean): whether to check arguments before generating
           vectors.
    """
    if check:
        assert is_number(center), LOGGER.error("center must be a number")
        center = FLOAT_TYPE(center)
        assert is_number(FWHM), LOGGER.error("FWHM must be a number")
        FWHM = FLOAT_TYPE(FWHM)
        assert FWHM>0, LOGGER.error("FWHM must be bigger than 0")
        assert isinstance(normalize, bool), LOGGER.error("normalize must be boolean")
    sigma       = FWHM/(2.*np.sqrt(2*np.log(2)))
    expKernel   = ((x-center)**2) / (-2*sigma**2)
    exp         = np.exp(expKernel)
    scaleFactor = 1.
    if normalize:
        scaleFactor /= sigma*np.sqrt(2*np.pi)
    return (scaleFactor * exp).astype(FLOAT_TYPE)


def step_function(x, center=0, FWHM=0.1, height=1, check=True):
    """
    Compute a step function as the cumulative summation of a gaussian
    distribution of a given vector.

    :Parameters:
        #. x (numpy.ndarray): The vector to compute the gaussian. gaussian
           is computed as a function of x.
        #. center (number): The center of the step function which is the
           the center of the gaussian.
        #. FWHM (number): The Full Width at Half Maximum of the gaussian.
        #. height (number): The height of the step function.
        #. check (boolean): whether to check arguments before generating
           vectors.
    """
    if check:
        assert is_number(height), LOGGER.error("height must be a number")
        height = FLOAT_TYPE(height)
    g  = gaussian(x, center=center, FWHM=FWHM, normalize=False, check=check)
    sf = np.cumsum(g)
    sf /= sf[-1]
    return (sf*height).astype(FLOAT_TYPE)


class ListenerBase(object):
    """All listeners base class."""
    def __init__(self):
        self.__listenerId = str(uuid.uuid1())

    @property
    def listenerId(self):
        """ Listener unique id set at initialization"""
        return self.__listenerId

    def listen(self, message, argument=None):
        """
        Listens to any message sent from the Broadcaster.

        :Parameters:
            #. message (object): Any python object to send to constraint's listen method.
            #. arguments (object): Any python object.
        """
        pass



class _Container(object):
    """
    This is a general objects container that is used by the engine to
    contain a unique instance for all objects that are prone for redundancy
    such as swapLists in SwapGenerators.
    """
    # This is for internal usage only
    __FIRST_INIT = True

    def __new__(cls, *args, **kwargs):
        #Singleton interface
        thisSingleton = cls.__dict__.get("_thisSingleton__")
        if thisSingleton is not None:
            return thisSingleton
        cls._thisSingleton__ = thisSingleton = object.__new__(cls,  *args, **kwargs)
        return thisSingleton

    def __init__(self):
        # this if statment insures initializing _Container only once.
        if _Container.__FIRST_INIT:
            self.__containers = {}
            self.__hints      = {}
            _Container.__FIRST_INIT = False

    def __getstate__(self):
        """no need to store hints dict"""
        self.__hints = {}
        return self.__dict__

    @property
    def containersName(self):
        """The containers name list."""
        return list(self.__containers)

    @property
    def containers(self):
        """The containers dictionary"""
        return self.__containers

    @property
    def hints(self):
        """The containers dictionary"""
        return self.__hints

    def get_location_by_hint(self, hint):
        """
        Get stored object in container using a hint.

        :Parameters:
           #. hint (object): This is used to fetch for stored object.
              Sometimes objects are parsed and modified before being set.
              In this particular case, those object will be passed as hint
              and then later used to find stored object after modification.

        :Returns:
            #. location (None, tuple): The object location given a hint.
               If hint not found, the None is returned
        """
        for location in self.__hints:
            h = self.__hints[location]
            if h is hint:
                return location
        # return None when nothing is found
        return None

    def is_container(self, name):
        """
        Check whether container exists given its name.

        :Parameters:
            #. name (string): The container's name.

        :Returns:
            #. result (boolean): Whether container exists.
        """
        return name in self.__containers

    def assert_location(self, location):
        """
        Checks location exists. If it doesn't, an error will be raised

        :Parameters:
            #. location (tuple): Location tuple as (name, key) that points
               to the value. It's typically implemented as such
               containers[name][key]
        """
        assert isinstance(location, (list, tuple)), LOGGER.error("location must be a tuple")
        assert len(location) == 2, LOGGER.error("location must contain 2 items")
        name, uniqueKey = location
        assert self.is_container(name), LOGGER.error("container name '%s' doesn't exists"%name)
        assert uniqueKey in self.__containers[name], LOGGER.error("container name '%s' key '%s' doesn't exist"%(name,uniqueKey))

    def add_container(self, name):
        """
        Add a container to the containers dict.

        :Parameters:
            #. name (string): The container's name.
        """
        assert isinstance(name, basestring), "name must be a string"
        assert not self.is_container(name), LOGGER.error("container name '%s' already exists"%name)
        self.__containers[name] = {}

    def pop_container(self, name):
        """
        Pop and return a containerfrom containers dict.

        :Parameters:
            #. name (string): The container's name.

        :Returns:
            #. value (list): The container value.
        """
        assert isinstance(name, basestring), "name must be a string"
        assert self.is_container(name), LOGGER.error("container name '%s' doesn't exists"%name)
        return self.__containers.pop(name)

    def add_to_container(self, container, value, hint=None):
        """
        Add a value to a container. If stored correctly a location tuple
        (name, uuid) will be returned. This location tuple is needed to locate
        and get the data when needed.

        :Parameters:
            #. container (string): The container's name.
            #. value (object): the value object to add to the container's.
            #. hint (object): hint used to fetch for stored object.
               Sometimes objects are parsed and modified before being set.
               In this particular case, those object will be passed as hint
               and then later used to find stored object after modification.

        :Returns:
            #. location (tuple): Location tuple as (container, key) that
               points to the value. It's typically implemented as such
               containers[container][key]
        """
        assert self.is_container(container), LOGGER.error("container name '%s' doesn't exists"%container)
        uniqueKey = str(uuid.uuid1())
        self.__containers[container][uniqueKey] = value
        # create location
        location = (container, uniqueKey)
        # add hint
        if hint is not None:
            self.__hints[location] = hint
        # return location
        return location

    def set_value(self, *args, **kwargs):
        """alias to add_to_container"""
        return self.add_to_container(*args, **kwargs)

    def get_value(self, location):
        """
        Get stored value in container.

        :Parameters:
            #. location (tuple): Location tuple as (name, key) that points
               to the value. It's typically implemented as such
               containers[name][key]

        :Returns:
            #. value (object): the value object to add to the container's list.

        """
        self.assert_location(location)
        name, uniqueKey = location
        return self.__containers[name][uniqueKey]

    def update_value(self, location, value):
        """
        Udpdate an existing value.

        :Parameters:
            #. location (tuple): Location tuple as (name, key) that points to
               the value. It's typically implemented as such
               containers[name][key]
            #. value (object): the value object to add to the container's.
        """
        self.assert_location(location)
        name, uniqueKey = location
        self.__containers[name][uniqueKey] = value
_Container()



class _AtomsCollector(object):
    """
    Atoms collector manages collecting atoms data whenever they are
    removed from from system. This mechanism allows storing and recovering
    atoms data at engine runtime.

    :Parameters:
        #. dataKeys (None, list): The data keys list promised to store
           everytime an atom is removed from the system. If None is given,
           dataKeys must be set later using set_data_keys method.
    """
    # internal usage only
    def __init__(self, parent, dataKeys=None):
        # set parent
        assert callable( getattr(parent, "_on_collector_collect_atom", None) ), LOGGER.error("_AtomsCollector parent must have '_on_collector_collect_atom' method")
        assert callable( getattr(parent, "_on_collector_release_atom", None) ), LOGGER.error("_AtomsCollector parent must have '_on_collector_release_atom' method")
        assert callable( getattr(parent, "_on_collector_reset", None) ), LOGGER.error("_AtomsCollector parent must have '_on_collector_reset' method")
        self.__parent = parent
        # set data keys tuple
        self.__dataKeys = ()
        if dataKeys is not None:
            self.set_data_keys(dataKeys)
        # set all properties
        self.reset()

    def __len__(self):
        return len(self.__collectedData)

    @property
    def dataKeys(self):
        """Data keys that this collector will collect."""
        return self.__dataKeys

    @property
    def indexes(self):
        """Collected atoms indexes."""
        return list(self.__collectedData)

    @property
    def indexesSortedArray(self):
        """Collected atoms sorted indexes numpy array."""
        return self.__indexesSortedArray

    @property
    def state(self):
        """Current collector state that will only change upon reseting,
        collecting or releasing atoms."""
        return self.__state

    def reset(self):
        """
        Reset collector to initial state by releasing all collected atoms
        and re-initializing all properties. parent._on_collector_reset
        method is not called.
        """
        # init indexes sorted array
        self.__indexesSortedArray = np.array([])
        # initialize collected data dictionary
        self.__collectedData = {}
        # set random data that can be used to collect random data at any time.
        # must be used only internally.
        self._randomData = None
        # set state
        self.__state = str(uuid.uuid1())

    def get_collected_data(self):
        """
        Get stored collected data.

        :Returns:
            #. collectedData (dict): The collected data dictionary.
        """
        return self.__collectedData

    def is_collected(self, index):
        """
        Get whether atom is collected given its index.

        :Parameters:
            #. index (int): The atom index to check whether it is
               collected or not.

        :Returns:
            #. result (bool): Whether it is collected or not.
        """
        return index in self.__collectedData

    def is_not_collected(self, index):
        """
        Get whether atom is not collected given its index.

        :Parameters:
            #. index (int): The atom index to check whether it is
               collected or not.

        :Returns:
            #. result (bool): Whether it is not collected or it is.
        """
        return not index in self.__collectedData

    def are_collected(self, indexes):
        """
        Get whether atoms are collected given their indexes.

        :Parameters:
            #. indexes (list,set,tuple, numpy.ndarray): Atoms indexes to
               check whether they are collected or not.

        :Returns:
            #. result (list): List of booleans defining whether atoms are
               collected or not.
        """
        return [idx in self.__collectedData for idx in indexes]

    def any_collected(self, indexes):
        """
        Get whether any atom in indexes is collected.

        :Parameters:
            #. indexes (list,set,tuple, numpy.ndarray): Atoms indexes to
               check whether they are collected or not.

        :Returns:
            #. result (boolean): Whether any collected atom is found collected.
        """
        for idx in indexes:
            if idx in self.__collectedData:
                return True
        return False

    def any_not_collected(self, indexes):
        """
        Get whether any atom in indexes is not collected.

        :Parameters:
            #. indexes (list,set,tuple, numpy.ndarray): Atoms indexes to
               check whether they are collected or not.

        :Returns:
            #. result (boolean): Whether any collected atom is not found
               collected.
        """
        for idx in indexes:
            if not idx in self.__collectedData:
                return True
        return False

    def all_collected(self, indexes):
        """
        Get whether all atoms in indexes are collected.

        :Parameters:
            #. indexes (list,set,tuple, numpy.ndarray): Atoms indexes to
               check whether they are collected or not.

        :Returns:
            #. result (boolean): Whether all atoms are collected.
        """
        for idx in indexes:
            if not idx in self.__collectedData:
                return False
        return True

    def all_not_collected(self, indexes):
        """
        Get whether all atoms in indexes are not collected.

        :Parameters:
            #. indexes (list,set,tuple, numpy.ndarray): Atoms indexes to
               check whether they are collected or not.

        :Returns:
            #. result (boolean): Whether all atoms are not collected.
        """
        for idx in indexes:
            if idx in self.__collectedData:
                return False
        return True

    def are_not_collected(self, indexes):
        """
        Get whether atoms are not collected given their indexes.

        :Parameters:
            #. indexes (list,set,tuple, numpy.ndarray): Atoms indexes to
               check whether they are collected or not.

        :Returns:
            #. result (list): List of booleans defining whether atoms are
               not collected or they are.
        """
        return [not idx in self.__collectedData for idx in indexes]

    def set_data_keys(self, dataKeys):
        """
        Set atoms collector data keys. keys can be set only once.
        This method will throw an error if used to reset dataKeys.

        :Parameters:
            #. dataKeys (list): The data keys list promised to store everytime
               an atom is removed from the system.
        """
        assert not len(self.__dataKeys), LOGGER.error("resetting dataKeys is not allowed")
        assert isinstance(dataKeys, (list, set, tuple)), LOGGER.error("dataKeys must be a list")
        assert len(set(dataKeys))==len(dataKeys),  LOGGER.error("Redundant keys in dataKeys list are found")
        assert len(dataKeys)>0,  LOGGER.error("dataKeys must not be empty")
        self.__dataKeys = tuple(sorted(dataKeys))

    def get_relative_index(self, index):
        """
        Compute relative atom index considering already collected atoms.

        :Parameters:
            #. index (int): Atom index.

        :Returns:
            #. relativeIndex (int): Atom relative index.
        """
        position = np.searchsorted(a=self.__indexesSortedArray, v=index, side='left').astype(INT_TYPE)
        return index-position

    def get_relative_indexes(self, indexes):
        """
        Compute relative atoms index considering already collected atoms.

        :Parameters:
            #. indexes (list,set,tuple,numpy.ndarray): Atoms index.

        :Returns:
            #. relativeIndexes (list): Atoms relative index.
        """
        positions = np.searchsorted(a=self.__indexesSortedArray, v=indexes, side='left').astype(INT_TYPE)
        return indexes-positions

    def get_real_index(self, relativeIndex):
        """
        Compute real index of the given relativeIndex considering
        already collected indexes.

        :Parameters:
            #. relativeIndex (int): Atom relative index to already collected
               indexes.

        :Parameters:
            #. index (int): Atom real index.
        """
        ### THIS IS NOT TESTED YET.
        indexes = np.array( sorted(self.indexes) )
        shift   = np.searchsorted(a=indexes, v=relativeIndex, side='left')
        index   = relativeIndex+shift
        for idx in indexes[shift:]:
            if idx > index:
                break
            index += 1
        return index

    def get_atom_data(self, index):
        """
        Get collected atom data.

        :Parameters:
            #. index (int): The atom index to return its collected data.
        """
        return self.__collectedData[index]

    def get_data_by_key(self, key):
        """
        Get all collected atoms data that is associated with a key.

        :Parameters:
            #. key (int): the data key.

        :Parameters:
            #. data (dict): dictionary of atoms indexes where values are the collected data.
        """
        data = {}
        for k in self.__collectedData:
            data[k] = self.__collectedData[k][key]
        return data

    def collect(self, index, dataDict, check=True):
        """
        Collect atom given its index.

        :Parameters:
            #. index (int): The atom index to collect.
            #. dataDict (dict): The atom data dict to collect.
            #. check (boolean):  Whether to check dataDict keys before
               collecting. If set to False, user promises that collected
               data is a dictionary and contains the needed keys.
        """
        assert not self.is_collected(index), LOGGER.error("attempting to collect and already collected atom of index '%i'"%index)
        # add data
        if check:
            assert isinstance(dataDict, dict), LOGGER.error("dataDict must be a dictionary of data where keys are dataKeys")
            assert tuple(sorted(dataDict)) == self.__dataKeys, LOGGER.error("dataDict keys don't match promised dataKeys")
        self.__collectedData[index] = dataDict
        # set indexes sorted array
        idx = np.searchsorted(a=self.__indexesSortedArray, v=index, side='left')
        self.__indexesSortedArray = np.insert(self.__indexesSortedArray, idx, index)
        # set state
        self.__state = str(uuid.uuid1())

    def release(self, index):
        """
        Release atom from list of collected atoms and return its
        collected data.

        :Parameters:
            #. index (int): The atom index to release.

        :Returns:
            #. dataDict (dict): The released atom collected data.
        """
        if not self.is_collected(index):
            LOGGER.warn("Attempting to release atom %i that is not collected."%index)
            return
        index = self.__collectedData.pop(index)
        # set indexes sorted array
        idx = np.searchsorted(a=self.__indexesSortedArray, v=index, side='left')
        self.__indexesSortedArray = np.insert(self.__indexesSortedArray, idx, index)
        # set state
        self.__state = str(uuid.uuid1())
        # return
        return index


class Broadcaster(object):
    """
    A broadcaster broadcasts a message to all registered listener.
    """
    def __init__(self):
        self.__listeners = []

    @property
    def listeners(self):
        """Listeners list copy."""
        return [l for l in self.__listeners]

    def add_listener(self, listener):
        """
        Add listener to the list of listeners.

        :Parameters:
            #. listener (object): Any python object having a listen method.
        """
        assert isinstance(listener, ListenerBase), LOGGER.error("listener must be a ListenerBase instance.")
        if listener not in self.__listeners:
            self.__listeners.append(listener)
        else:
            LOGGER.warn("listener already exist in broadcaster list")

    def remove_listener(self, listener):
        """
        Remove listener to the list of listeners.

        :Parameters:
            #. listener (object): The listener object to remove.
        """
        assert isinstance(listener, ListenerBase), LOGGER.error("listener must be a ListenerBase instance.")
        # remove listener
        self.__listeners = [l for l in self.__listeners if l.listenerId != listener.listenerId]

    def broadcast(self, message, arguments=None):
        """
        Broadcast a message to all the listeners

        :Parameters:
            #. message (object): Any type of message object to pass to
               the listeners.
            #. arguments (object): Any type of argument to pass to the
               listeners.
        """
        for l in self.__listeners:
            l.listen(message, arguments)


class RandomFloatGenerator(object):
    """
    Generate random float number between a lower and an upper limit.

    :Parameters:
        #. lowerLimit (number): The lower limit allowed.
        #. upperLimit (number): The upper limit allowed.
    """
    def __init__(self, lowerLimit, upperLimit):
         self.__lowerLimit = None
         self.__upperLimit = None
         self.set_lower_limit(lowerLimit)
         self.set_upper_limit(upperLimit)

    @property
    def lowerLimit(self):
        """Lower limit of the number generation."""
        return self.__lowerLimit

    @property
    def upperLimit(self):
        """Upper limit of the number generation."""
        return self.__upperLimit

    @property
    def rang(self):
        """Range defined as upperLimit-lowerLimit."""
        return self.__rang

    def set_lower_limit(self, lowerLimit):
        """
        Set lower limit.

        :Parameters:
            #. lowerLimit (number): Lower limit allowed.
        """
        assert is_number(lowerLimit), LOGGER.error("lowerLimit must be numbers")
        self.__lowerLimit = FLOAT_TYPE(lowerLimit)
        if self.__upperLimit is not None:
            assert self.__lowerLimit<self.__upperLimit, LOGGER.error("lower limit must be smaller than the upper one")
            self.__rang = FLOAT_TYPE(self.__upperLimit-self.__lowerLimit)

    def set_upper_limit(self, upperLimit):
        """
        Set upper limit.

        :Parameters:
            #. upperLimit (number): Upper limit allowed.
        """
        assert is_number(upperLimit), LOGGER.error("upperLimit must be numbers")
        self.__upperLimit = FLOAT_TYPE(upperLimit)
        if self.__lowerLimit is not None:
            assert self.__lowerLimit<self.__upperLimit, LOGGER.error("lower limit must be smaller than the upper one")
            self.__rang = FLOAT_TYPE(self.__upperLimit-self.__lowerLimit)

    def generate(self):
        """Generate a random float number between lowerLimit and upperLimit."""
        return FLOAT_TYPE(self.__lowerLimit+generate_random_float()*self.__rang)


class BiasedRandomFloatGenerator(RandomFloatGenerator):
    """
    Generate biased random float number between a lower and an upper limit.
    To bias the generator at a certain number, a bias gaussian is added to the
    weights scheme at the position of this particular number.

    .. image:: biasedFloatGenerator.png
       :align: center

    :Parameters:
        #. lowerLimit (number): The lower limit allowed.
        #. upperLimit (number): The upper limit allowed.
        #. weights (None, list, numpy.ndarray): The weights scheme.
           The length defines the number of bins and the edges.
           The length of weights array defines the resolution of the biased
           numbers generation. If None is given, ones array of length 10000
           is automatically generated.
        #. biasRange(None, number): The bias gaussian range.
           It must be smaller than half of limits range which is equal to
           (upperLimit-lowerLimit)/2. If None is given, it will be
           automatically set to (upperLimit-lowerLimit)/5
        #. biasFWHM(None, number): The bias gaussian Full Width at Half Maximum.
           It must be smaller than half of biasRange.
           If None, it will be automatically set to biasRange/10
        #. biasHeight(number): The bias gaussian maximum intensity.
        #. unbiasRange(None, number): The bias gaussian range.
           It must be smaller than half of limits range which is equal to
           (upperLimit-lowerLimit)/2. If None is given, it will be
           automatically set to biasRange.
        #. unbiasFWHM(None, number): The bias gaussian Full Width at Half
           Maximum. It must be smaller than half of biasRange.
           If None is given, it will be automatically set to biasFWHM.
        #. unbiasHeight(number): The unbias gaussian maximum intensity.
           If None is given, it will be automatically set to biasHeight.
        #. unbiasThreshold(number): unbias is only applied at a certain
           position only when the position weight is above unbiasThreshold.
           It must be a positive number.
    """
    def __init__(self, lowerLimit, upperLimit,
                       weights=None,
                       biasRange=None, biasFWHM=None, biasHeight=1,
                       unbiasRange=None, unbiasFWHM=None, unbiasHeight=None, unbiasThreshold=1):
         # initialize random generator
         super(BiasedRandomFloatGenerator, self).__init__(lowerLimit=lowerLimit, upperLimit=upperLimit)
         # set scheme
         self.set_weights(weights)
         # set bias function
         self.set_bias(biasRange=biasRange, biasFWHM=biasFWHM, biasHeight=biasHeight)
         # set unbias function
         self.set_unbias(unbiasRange=unbiasRange, unbiasFWHM=unbiasFWHM, unbiasHeight=unbiasHeight, unbiasThreshold=unbiasThreshold)

    @property
    def originalWeights(self):
        """Original weights as initialized."""
        return self.__originalWeights

    @property
    def weights(self):
        """Current value weights vector."""
        weights = self.__scheme[1:]-self.__scheme[:-1]
        weights = list(weights)
        weights.insert(0,self.__scheme[0])
        return weights

    @property
    def scheme(self):
        """Numbers generation scheme."""
        return self.__scheme

    @property
    def bins(self):
        """Number of bins that is equal to the length of weights vector."""
        return self.__bins

    @property
    def binWidth(self):
        """Bin width defining the resolution of the biased random
        number generation."""
        return self.__binWidth

    @property
    def bias(self):
        """Bias step-function."""
        return self.__bias

    @property
    def biasGuassian(self):
        """Bias gaussian function."""
        return self.__biasGuassian

    @property
    def biasRange(self):
        """Bias gaussian extent range."""
        return self.__biasRange

    @property
    def biasBins(self):
        """Bias gaussian number of bins."""
        return self.__biasBins

    @property
    def biasFWHM(self):
        """Bias gaussian Full Width at Half Maximum."""
        return self.__biasFWHM

    @property
    def biasFWHMBins(self):
        """Bias gaussian Full Width at Half Maximum number of bins."""
        return self.__biasFWHMBins

    @property
    def unbias(self):
        """Unbias step-function."""
        return self.__unbias

    @property
    def unbiasGuassian(self):
        """Unbias gaussian function."""
        return self.__unbiasGuassian

    @property
    def unbiasRange(self):
        """Unbias gaussian extent range."""
        return self.__unbiasRange

    @property
    def unbiasBins(self):
        """Unbias gaussian number of bins."""
        return self.__unbiasBins

    @property
    def unbiasFWHM(self):
        """Unbias gaussian Full Width at Half Maximum."""
        return self.__unbiasFWHM

    @property
    def unbiasFWHMBins(self):
        """Unbias gaussian Full Width at Half Maximum number of bins."""
        return self.__unbiasFWHMBins

    def set_weights(self, weights=None):
        """
        Set generator's weights.

        :Parameters:
            #. weights (None, list, numpy.ndarray): The weights scheme.
               The length defines the number of bins and the edges.
               The length of weights array defines the resolution of the
               biased numbers generation. If None is given, ones array of
               length 10000 is automatically generated.
        """
        # set original weights
        if weights is None:
           self.__bins = 10000
           self.__originalWeights = np.ones(self.__bins)
        else:
            assert isinstance(weights, (list, set, tuple, np.ndarray)), LOGGER.error("weights must be a list of numbers")
            if isinstance(weights,  np.ndarray):
                assert len(weights.shape)==1, LOGGER.error("weights must be uni-dimensional")
            wgts = []
            assert len(weights)>=100, LOGGER.error("weights minimum length allowed is 100")
            for w in weights:
                assert is_number(w), LOGGER.error("weights items must be numbers")
                w = FLOAT_TYPE(w)
                assert w>=0, LOGGER.error("weights items must be positive")
                wgts.append(w)
            self.__originalWeights = np.array(wgts, dtype=FLOAT_TYPE)
            self.__bins = len(self.__originalWeights)
        # set bin width
        self.__binWidth     = FLOAT_TYPE(self.rang/self.__bins)
        self.__halfBinWidth = FLOAT_TYPE(self.__binWidth/2.)
        # set scheme
        self.__scheme = np.cumsum( self.__originalWeights )

    def set_bias(self, biasRange, biasFWHM, biasHeight):
        """
        Set generator's bias gaussian function

        :Parameters:
            #. biasRange(None, number): Bias gaussian range. It must be
               smaller than half of limits range which is equal to
               (upperLimit-lowerLimit)/2. If None is given, it will
               be automatically set to (upperLimit-lowerLimit)/5.
            #. biasFWHM(None, number): Bias gaussian Full Width at Half
               Maximum. It must be smaller than half of biasRange.
               If None is given, it will be automatically set to biasRange/10.
            #. biasHeight(number): Bias gaussian maximum intensity.
        """
        # check biasRange
        if biasRange is None:
            biasRange = FLOAT_TYPE(self.rang/5.)
        else:
            assert is_number(biasRange), LOGGER.error("biasRange must be numbers")
            biasRange = FLOAT_TYPE(biasRange)
            assert biasRange>0, LOGGER.error("biasRange must be positive")
            assert biasRange<=self.rang/2., LOGGER.error("biasRange must be smaller than 50%% of limits range which is %s in this case"%str(self.rang))
        self.__biasRange = FLOAT_TYPE(biasRange)
        self.__biasBins  = INT_TYPE(self.bins*self.__biasRange/self.rang)
        # check biasFWHM
        if biasFWHM is None:
            biasFWHM = FLOAT_TYPE(self.__biasRange/10.)
        else:
            assert is_number(biasFWHM), LOGGER.error("biasFWHM must be numbers")
            biasFWHM = FLOAT_TYPE(biasFWHM)
            assert biasFWHM>=0, LOGGER.error("biasFWHM must be positive")
            assert biasFWHM<=self.__biasRange/2., LOGGER.error("biasFWHM must be smaller than 50%% of bias range which is %s in this case"%str(self.__biasRange))
        self.__biasFWHM     = FLOAT_TYPE(biasFWHM)
        self.__biasFWHMBins = INT_TYPE(self.bins*self.__biasFWHM/self.rang)
        # check height
        assert is_number(biasHeight), LOGGER.error("biasHeight must be a number")
        self.__biasHeight = FLOAT_TYPE(biasHeight)
        assert self.__biasHeight>=0, LOGGER.error("biasHeight must be positive")
        # create bias step function
        b = self.__biasRange/self.__biasBins
        x = [-self.__biasRange/2.+idx*b for idx in range(self.__biasBins) ]
        self.__biasGuassian = gaussian(x, center=0, FWHM=self.__biasFWHM, normalize=False)
        self.__biasGuassian -= self.__biasGuassian[0]
        self.__biasGuassian /= np.max(self.__biasGuassian)
        self.__biasGuassian *= self.__biasHeight
        self.__bias = np.cumsum(self.__biasGuassian)

    def set_unbias(self, unbiasRange, unbiasFWHM, unbiasHeight, unbiasThreshold):
        """
        Set generator's unbias gaussian function

        :Parameters:
            #. unbiasRange(None, number): The bias gaussian range.
               It must be smaller than half of limits range which is equal to
               (upperLimit-lowerLimit)/2. If None, it will be automatically set
               to biasRange.
            #. unbiasFWHM(None, number): The bias gaussian Full Width at Half
               Maximum. It must be smaller than half of biasRange.
               If None is given, it will be automatically set to biasFWHM.
            #. unbiasHeight(number): The unbias gaussian maximum intensity.
               If None is given, it will be automatically set to biasHeight.
            #. unbiasThreshold(number): unbias is only applied at a certain
               position only when the position weight is above
               unbiasThreshold. It must be a positive number.
        """
        # check biasRange
        if unbiasRange is None:
            unbiasRange = self.__biasRange
        else:
            assert is_number(unbiasRange), LOGGER.error("unbiasRange must be numbers")
            unbiasRange = FLOAT_TYPE(unbiasRange)
            assert unbiasRange>0, LOGGER.error("unbiasRange must be positive")
            assert unbiasRange<=self.rang/2., LOGGER.error("unbiasRange must be smaller than 50%% of limits range which is %s in this case"%str(self.rang))
        self.__unbiasRange = FLOAT_TYPE(unbiasRange)
        self.__unbiasBins  = INT_TYPE(self.bins*self.__unbiasRange/self.rang)
        # check biasFWHM
        if unbiasFWHM is None:
            unbiasFWHM = self.__biasFWHM
        else:
            assert is_number(unbiasFWHM), LOGGER.error("unbiasFWHM must be numbers")
            unbiasFWHM = FLOAT_TYPE(unbiasFWHM)
            assert unbiasFWHM>=0, LOGGER.error("unbiasFWHM must be positive")
            assert unbiasFWHM<=self.__unbiasRange/2., LOGGER.error("unbiasFWHM must be smaller than 50%% of bias range which is %s in this case"%str(self.__biasRange))
        self.__unbiasFWHM     = FLOAT_TYPE(unbiasFWHM)
        self.__unbiasFWHMBins = INT_TYPE(self.bins*self.__unbiasFWHM/self.rang)
        # check height
        if unbiasHeight is None:
            unbiasHeight = self.__biasHeight
        assert is_number(unbiasHeight), LOGGER.error("unbiasHeight must be a number")
        self.__unbiasHeight = FLOAT_TYPE(unbiasHeight)
        assert self.__unbiasHeight>=0, LOGGER.error("unbiasHeight must be bigger than 0")
        # check unbiasThreshold
        assert is_number(unbiasThreshold), LOGGER.error("unbiasThreshold must be a number")
        self.__unbiasThreshold = FLOAT_TYPE(unbiasThreshold)
        assert self.__unbiasThreshold>=0, LOGGER.error("unbiasThreshold must be positive")
        # create bias step function
        b = self.__unbiasRange/self.__unbiasBins
        x = [-self.__unbiasRange/2.+idx*b for idx in range(self.__unbiasBins) ]
        self.__unbiasGuassian = gaussian(x, center=0, FWHM=self.__unbiasFWHM, normalize=False)
        self.__unbiasGuassian -= self.__unbiasGuassian[0]
        self.__unbiasGuassian /= np.max(self.__unbiasGuassian)
        self.__unbiasGuassian *= -self.__unbiasHeight
        self.__unbias = np.cumsum(self.__unbiasGuassian)

    def bias_scheme_by_index(self, index, scaleFactor=None, check=True):
        """
        Bias the generator's scheme using the defined bias gaussian
        function at the given index.

        :Parameters:
            #. index(integer): The index of the position to bias
            #. scaleFactor(None, number): Whether to scale the bias gaussian
               before biasing the scheme. If None is given, bias gaussian is
               used as defined.
            #. check(boolean): Whether to check arguments.
        """
        if not self.__biasHeight>0: return
        if check:
            assert is_integer(index), LOGGER.error("index must be an integer")
            index = INT_TYPE(index)
            assert index>=0, LOGGER.error("index must be bigger than 0")
            assert index<=self.__bins, LOGGER.error("index must be smaller than number of bins")
            if scaleFactor is not None:
                assert is_number(scaleFactor), LOGGER.error("scaleFactor must be a number")
                scaleFactor = FLOAT_TYPE(scaleFactor)
                assert scaleFactor>=0, LOGGER.error("scaleFactor must be bigger than 0")
        # get start indexes
        startIdx = index-int(self.__biasBins/2)
        if startIdx < 0:
            biasStartIdx = -startIdx
            startIdx = 0
            bias = np.cumsum(self.__biasGuassian[biasStartIdx:]).astype(FLOAT_TYPE)
        else:
            biasStartIdx = 0
            bias = self.__bias
        # scale bias
        if scaleFactor is None:
            scaledBias = bias
        else:
            scaledBias = bias*scaleFactor
        # get end indexes
        endIdx = startIdx+self.__biasBins-biasStartIdx
        biasEndIdx = len(scaledBias)
        if endIdx > self.__bins-1:
            biasEndIdx -= endIdx-self.__bins
            endIdx = self.__bins
        # bias scheme
        self.__scheme[startIdx:endIdx] += scaledBias[0:biasEndIdx]
        self.__scheme[endIdx:] += scaledBias[biasEndIdx-1]

    def bias_scheme_at_position(self, position, scaleFactor=None, check=True):
        """
        Bias the generator's scheme using the defined bias gaussian function
        at the given number.

        :Parameters:
            #. position(number): The number to bias.
            #. scaleFactor(None, number): Whether to scale the bias gaussian
               before biasing the scheme. If None is given, bias gaussian is
               used as defined.
            #. check(boolean): Whether to check arguments.
        """
        if check:
            assert is_number(position), LOGGER.error("position must be a number")
            position = FLOAT_TYPE(position)
            assert position>=self.lowerLimit, LOGGER.error("position must be bigger than lowerLimit")
            assert position<=self.upperLimit, LOGGER.error("position must be smaller than upperLimit")
        index = INT_TYPE(self.__bins*(position-self.lowerLimit)/self.rang)
        # bias scheme by index
        self.bias_scheme_by_index(index=index, scaleFactor=scaleFactor, check=check)

    def unbias_scheme_by_index(self, index, scaleFactor=None, check=True):
        """
        Unbias the generator's scheme using the defined bias gaussian
        function at the given index.

        :Parameters:
            #. index(integer): The index of the position to unbias.
            #. scaleFactor(None, number): Whether to scale the unbias gaussian
               before unbiasing the scheme. If None is given, unbias gaussian
               is used as defined.
            #. check(boolean): Whether to check arguments.
        """
        if not self.__unbiasHeight>0: return
        if check:
            assert is_integer(index), LOGGER.error("index must be an integer")
            index = INT_TYPE(index)
            assert index>=0, LOGGER.error("index must be bigger than 0")
            assert index<=self.__bins, LOGGER.error("index must be smaller than number of bins")
            if scaleFactor is not None:
                assert is_number(scaleFactor), LOGGER.error("scaleFactor must be a number")
                scaleFactor = FLOAT_TYPE(scaleFactor)
                assert scaleFactor>=0, LOGGER.error("scaleFactor must be bigger than 0")
        # get start indexes
        startIdx = index-int(self.__unbiasBins/2)
        if startIdx < 0:
            biasStartIdx = -startIdx
            startIdx = 0
            unbias = self.__unbiasGuassian[biasStartIdx:]
        else:
            biasStartIdx = 0
            unbias = self.__unbiasGuassian
        # get end indexes
        endIdx = startIdx+self.__unbiasBins-biasStartIdx
        biasEndIdx = len(unbias)
        if endIdx > self.__bins-1:
            biasEndIdx -= endIdx-self.__bins
            endIdx = self.__bins
        # scale unbias
        if scaleFactor is None:
            scaledUnbias = unbias
        else:
            scaledUnbias = unbias*scaleFactor
        # unbias weights
        weights = np.array(self.weights)
        weights[startIdx:endIdx] += scaledUnbias[0:biasEndIdx]
        # correct for negatives
        weights[np.where(weights<self.__unbiasThreshold)] = self.__unbiasThreshold
        # set unbiased scheme
        self.__scheme = np.cumsum(weights)

    def unbias_scheme_at_position(self, position, scaleFactor=None, check=True):
        """
        Unbias the generator's scheme using the defined bias gaussian
        function at the given number.

        :Parameters:
            #. position(number): The number to unbias.
            #. scaleFactor(None, number): Whether to scale the unbias gaussian
               before unbiasing the scheme. If None is given, unbias gaussian
               is used as defined.
            #. check(boolean): Whether to check arguments.
        """
        if check:
            assert is_number(position), LOGGER.error("position must be a number")
            position = FLOAT_TYPE(position)
            assert position>=self.lowerLimit, LOGGER.error("position must be bigger than lowerLimit")
            assert position<=self.upperLimit, LOGGER.error("position must be smaller than upperLimit")
        index = INT_TYPE(self.__bins*(position-self.lowerLimit)/self.rang)
        # bias scheme by index
        self.unbias_scheme_by_index(index=index, scaleFactor=scaleFactor, check=check)

    def generate(self):
        """Generate a random float number between the biased range
        lowerLimit and upperLimit."""
        # get position
        position = self.lowerLimit + self.__binWidth*np.searchsorted(self.__scheme, generate_random_float()*self.__scheme[-1]) + self.__halfBinWidth
        # find limits
        minLim = max(self.lowerLimit, position-self.__halfBinWidth)
        maxLim = min(self.upperLimit, position+self.__halfBinWidth)
        # generate number
        return minLim+generate_random_float()*(maxLim-minLim) + self.__halfBinWidth


class RandomIntegerGenerator(object):
    """
    Generate random integer number between a lower and an upper limit.

    :Parameters:
        #. lowerLimit (number): Lower limit allowed.
        #. upperLimit (number): Upper limit allowed.
    """
    def __init__(self, lowerLimit, upperLimit):
         self.__lowerLimit = None
         self.__upperLimit = None
         self.set_lower_limit(lowerLimit)
         self.set_upper_limit(upperLimit)

    @property
    def lowerLimit(self):
        """Lower limit of the number generation."""
        return self.__lowerLimit

    @property
    def upperLimit(self):
        """Upper limit of the number generation."""
        return self.__upperLimit

    @property
    def rang(self):
        """The range defined as upperLimit-lowerLimit"""
        return self.__rang

    def set_lower_limit(self, lowerLimit):
        """
        Set lower limit.

        :Parameters:
            #. lowerLimit (number): The lower limit allowed.
        """
        assert is_integer(lowerLimit), LOGGER.error("lowerLimit must be numbers")
        self.__lowerLimit = INT_TYPE(lowerLimit)
        if self.__upperLimit is not None:
            assert self.__lowerLimit<self.__upperLimit, LOGGER.error("lower limit must be smaller than the upper one")
            self.__rang = self.__upperLimit-self.__lowerLimit+1

    def set_upper_limit(self, upperLimit):
        """
        Set upper limit.

        :Parameters:
            #. upperLimit (number): The upper limit allowed.
        """
        assert is_integer(upperLimit), LOGGER.error("upperLimit must be numbers")
        self.__upperLimit = INT_TYPE(upperLimit)
        if self.__lowerLimit is not None:
            assert self.__lowerLimit<self.__upperLimit, LOGGER.error("lower limit must be smaller than the upper one")
            self.__rang = self.__upperLimit-self.__lowerLimit+1

    def generate(self):
        """Generate a random integer number between lowerLimit and upperLimit."""
        return generate_random_integer(self.__lowerLimit, self.__upperLimit)


class BiasedRandomIntegerGenerator(RandomIntegerGenerator):
    """
    Generate biased random integer number between a lower and an upper limit.
    To bias the generator at a certain number, a bias height is added to the
    weights scheme at the position of this particular number.

    .. image:: biasedIntegerGenerator.png
       :align: center

    :Parameters:
        #. lowerLimit (integer): The lower limit allowed.
        #. upperLimit (integer): The upper limit allowed.
        #. weights (None, list, numpy.ndarray): The weights scheme.
           The length must be equal to the range between lowerLimit
           and upperLimit. If None is given, ones array of length
           upperLimit-lowerLimit+1 is automatically generated.
        #. biasHeight(number): The weight bias intensity.
        #. unbiasHeight(None, number): The weight unbias intensity.
           If None, it will be automatically set to biasHeight.
        #. unbiasThreshold(number): unbias is only applied at a certain
           position only when the position weight is above unbiasThreshold.
           It must be a positive number.
    """
    def __init__(self, lowerLimit, upperLimit,
                       weights=None,
                       biasHeight=1, unbiasHeight=None, unbiasThreshold=1):
        # initialize random generator
        super(BiasedRandomIntegerGenerator, self).__init__(lowerLimit=lowerLimit, upperLimit=upperLimit)
        # set weights
        self.set_weights(weights=weights)
        # set bias height
        self.set_bias_height(biasHeight=biasHeight)
        # set bias height
        self.set_unbias_height(unbiasHeight=unbiasHeight)
        # set bias height
        self.set_unbias_threshold(unbiasThreshold=unbiasThreshold)

    @property
    def originalWeights(self):
        """Original weights as initialized."""
        return self.__originalWeights

    @property
    def weights(self):
        """Current value weights vector."""
        weights = self.__scheme[1:]-self.__scheme[:-1]
        weights = list(weights)
        weights.insert(0,self.__scheme[0])
        return weights

    @property
    def scheme(self):
        """Numbers generation scheme."""
        return self.__scheme

    @property
    def bins(self):
        """Number of bins that is equal to the length of weights vector."""
        return self.__bins

    def set_weights(self, weights):
        """
        Set the generator integer numbers weights.

        :Parameters:
            #. weights (None, list, numpy.ndarray): The weights scheme.
               The length must be equal to the range between lowerLimit and
               upperLimit. If None is given, ones array of length
               upperLimit-lowerLimit+1 is automatically generated.
        """
        if weights is None:
            self.__originalWeights = np.ones(self.upperLimit-self.lowerLimit+1)
        else:
            assert isinstance(weights, (list, set, tuple, np.ndarray)), LOGGER.error("weights must be a list of numbers")
            if isinstance(weights,  np.ndarray):
                assert len(weights.shape)==1, LOGGER.error("weights must be uni-dimensional")
            wgts = []
            assert len(weights)==self.upperLimit-self.lowerLimit+1, LOGGER.error("weights length must be exactly equal to 'upperLimit-lowerLimit+1' which is %i"%self.upperLimit-self.lowerLimit+1)
            for w in weights:
                assert is_number(w), LOGGER.error("weights items must be numbers")
                w = FLOAT_TYPE(w)
                assert w>=0, LOGGER.error("weights items must be positive")
                wgts.append(w)
            self.__originalWeights = np.array(wgts, dtype=FLOAT_TYPE)
        # set bins
        self.__bins = len( self.__originalWeights )
        # set scheme
        self.__scheme = np.cumsum( self.__originalWeights )

    def set_bias_height(self, biasHeight):
        """
        Set weight bias intensity.

        :Parameters:
            #. biasHeight(number): Weight bias intensity.
        """
        assert is_number(biasHeight), LOGGER.error("biasHeight must be a number")
        self.__biasHeight = FLOAT_TYPE(biasHeight)
        assert self.__biasHeight>0, LOGGER.error("biasHeight must be bigger than 0")

    def set_unbias_height(self, unbiasHeight):
        """
        Set weight unbias intensity.

        :Parameters:
            #. unbiasHeight(None, number): The weight unbias intensity.
               If None, it will be automatically set to biasHeight.
        """
        if unbiasHeight is None:
            unbiasHeight = self.__biasHeight
        assert is_number(unbiasHeight), LOGGER.error("unbiasHeight must be a number")
        self.__unbiasHeight = FLOAT_TYPE(unbiasHeight)
        assert self.__unbiasHeight>=0, LOGGER.error("unbiasHeight must be positive")

    def set_unbias_threshold(self, unbiasThreshold):
        """
        Set weight unbias threshold.

        :Parameters:
            #. unbiasThreshold(number): unbias is only applied at a certain
               position only when the position weight is above unbiasThreshold.
               It must be a positive number.
        """
        assert is_number(unbiasThreshold), LOGGER.error("unbiasThreshold must be a number")
        self.__unbiasThreshold = FLOAT_TYPE(unbiasThreshold)
        assert self.__unbiasThreshold>=0, LOGGER.error("unbiasThreshold must be positive")

    def bias_scheme_by_index(self, index, scaleFactor=None, check=True):
        """
        Bias the generator's scheme at the given index.

        :Parameters:
            #. index(integer): The index of the position to bias
            #. scaleFactor(None, number): Whether to scale the bias gaussian
               before biasing the scheme. If None, bias gaussian is used as
               defined.
            #. check(boolean): Whether to check arguments.
        """
        if not self.__biasHeight>0: return
        if check:
            assert is_integer(index), LOGGER.error("index must be an integer")
            index = INT_TYPE(index)
            assert index>=0, LOGGER.error("index must be bigger than 0")
            assert index<=self.__bins, LOGGER.error("index must be smaller than number of bins")
            if scaleFactor is not None:
                assert is_number(scaleFactor), LOGGER.error("scaleFactor must be a number")
                scaleFactor = FLOAT_TYPE(scaleFactor)
                assert scaleFactor>=0, LOGGER.error("scaleFactor must be bigger than 0")
        # scale bias
        if scaleFactor is None:
            scaledBias = self.__biasHeight
        else:
            scaledBias = self.__biasHeight*scaleFactor
        # bias scheme
        self.__scheme[index:] += scaledBias

    def bias_scheme_at_position(self, position, scaleFactor=None, check=True):
        """
        Bias the generator's scheme at the given number.

        :Parameters:
            #. position(number): The number to bias.
            #. scaleFactor(None, number): Whether to scale the bias gaussian
               before biasing the scheme. If None, bias gaussian is used as
               defined.
            #. check(boolean): Whether to check arguments.
        """
        if check:
            assert is_integer(position), LOGGER.error("position must be an integer")
            position = INT_TYPE(position)
            assert position>=self.lowerLimit, LOGGER.error("position must be bigger than lowerLimit")
            assert position<=self.upperLimit, LOGGER.error("position must be smaller than upperLimit")
        index = position-self.lowerLimit
        # bias scheme by index
        self.bias_scheme_by_index(index=index, scaleFactor=scaleFactor, check=check)

    def unbias_scheme_by_index(self, index, scaleFactor=None, check=True):
        """
        Unbias the generator's scheme at the given index.

        :Parameters:
            #. index(integer): The index of the position to unbias
            #. scaleFactor(None, number): Whether to scale the unbias gaussian
               before unbiasing the scheme. If None is given,
               unbias gaussian is used as defined.
            #. check(boolean): Whether to check arguments.
        """
        if not self.__unbiasHeight>0: return
        if check:
            assert is_integer(index), LOGGER.error("index must be an integer")
            index = INT_TYPE(index)
            assert index>=0, LOGGER.error("index must be bigger than 0")
            assert index<=self.__bins, LOGGER.error("index must be smaller than number of bins")
            if scaleFactor is not None:
                assert is_number(scaleFactor), LOGGER.error("scaleFactor must be a number")
                scaleFactor = FLOAT_TYPE(scaleFactor)
                assert scaleFactor>=0, LOGGER.error("scaleFactor must be bigger than 0")
        # scale unbias
        if scaleFactor is None:
            scaledUnbias = self.__unbiasHeight
        else:
            scaledUnbias = self.__unbiasHeight*scaleFactor
        # check threshold
        if index == 0:
            scaledUnbias = max(scaledUnbias, self.__scheme[index]-self.__unbiasThreshold)
        elif self.__scheme[index]-scaledUnbias < self.__scheme[index-1]+self.__unbiasThreshold:
            scaledUnbias = self.__scheme[index]-self.__scheme[index-1]-self.__unbiasThreshold
        # unbias scheme
        self.__scheme[index:] -= scaledUnbias

    def unbias_scheme_at_position(self, position, scaleFactor=None, check=True):
        """
        Unbias the generator's scheme using the defined bias gaussian
        function at the given number.

        :Parameters:
            #. position(number): The number to unbias.
            #. scaleFactor(None, number): Whether to scale the unbias gaussian
               before unbiasing the scheme. If None is given, unbias
               gaussian is used as defined.
            #. check(boolean): Whether to check arguments.
        """
        if check:
            assert is_integer(position), LOGGER.error("position must be an integer")
            position = INT_TYPE(position)
            assert position>=self.lowerLimit, LOGGER.error("position must be bigger than lowerLimit")
            assert position<=self.upperLimit, LOGGER.error("position must be smaller than upperLimit")
        index = position-self.lowerLimit
        # unbias scheme by index
        self.unbias_scheme_by_index(index=index, scaleFactor=scaleFactor, check=check)

    def generate(self):
        """Generate a random intger number between the biased range
        lowerLimit and upperLimit."""
        index = INT_TYPE( np.searchsorted(self.__scheme, generate_random_float()*self.__scheme[-1]) )
        return self.lowerLimit + index

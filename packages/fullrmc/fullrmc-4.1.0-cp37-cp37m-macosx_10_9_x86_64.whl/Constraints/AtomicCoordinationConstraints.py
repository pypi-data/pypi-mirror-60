"""
AtomicCoordinationConstraints contains classes for all constraints related
to coordination number in spherical shells around atoms.

.. inheritance-diagram:: fullrmc.Constraints.AtomicCoordinationConstraints
    :parts: 1

"""
# standard libraries imports
from __future__ import print_function
import copy, re

# external libraries imports
import numpy as np

# fullrmc imports
from ..Globals import INT_TYPE, FLOAT_TYPE, PI, LOGGER
from ..Globals import str, long, unicode, bytes, basestring, range, xrange, maxint
from ..Core.Collection import is_number, is_integer, raise_if_collected, reset_if_collected_out_of_date
from ..Core.Collection import get_caller_frames
from ..Core.Constraint import SingularConstraint, RigidConstraint
from ..Core.atomic_coordination import all_atoms_coord_number_coords, multi_atoms_coord_number_coords


class AtomicCoordinationNumberConstraint(RigidConstraint, SingularConstraint):
    """
    It's a rigid constraint that controls the coordination number of atoms.

    .. raw:: html

        <iframe width="560" height="315"
        src="https://www.youtube.com/embed/R8t-_XwizOI?rel=0"
        frameborder="0" allowfullscreen>
        </iframe>


    +----------------------------------------------------------------------+
    |.. figure:: atomic_coordination_number_constraint_plot_method.png     |
    |   :width: 530px                                                      |
    |   :height: 400px                                                     |
    |   :align: left                                                       |
    +----------------------------------------------------------------------+


    :Parameters:
        #. rejectProbability (Number): rejecting probability of all steps
           where standardError increases. It must be between 0 and 1 where 1
           means rejecting all steps where standardError increases and 0 means
           accepting all steps regardless whether standardError increases or
           not.


    .. code-block:: python

        # import fullrmc modules
        from fullrmc.Engine import Engine
        from fullrmc.Constraints.AtomicCoordinationConstraints import AtomicCoordinationNumberConstraint

        # create engine
        ENGINE = Engine(path='my_engine.rmc')

        # set pdb file
        ENGINE.set_pdb('system.pdb')

        # create and add constraint
        ACNC = AtomicCoordinationNumberConstraint()
        ENGINE.add_constraints(ACNC)

        # create definition
        ACNC.set_coordination_number_definition( [ ('Al','Cl',1.5, 2.5, 2, 2),
                                                   ('Al','S', 2.5, 3.0, 2, 2)] )

    """
    def __init__(self, rejectProbability=1):
        # initialize constraint
        RigidConstraint.__init__(self, rejectProbability=rejectProbability)
        # set atomsColletors data keys
        self._atomsCollector.set_data_keys( ('coresIndexes', 'shellsIndexes',
                                             'asCoreDefIdxs', 'inShellDefIdxs') )
        # initialize data
        self.__initialize_constraint_data()
        # set coordination number definition
        self.set_coordination_number_definition(None)
        # set computation cost
        self.set_computation_cost(5.0)
        # set frame data
        FRAME_DATA = [d for d in self.FRAME_DATA]
        FRAME_DATA.extend(['_AtomicCoordinationNumberConstraint__coordNumDef',
                           '_AtomicCoordinationNumberConstraint__coresIndexes',
                           '_AtomicCoordinationNumberConstraint__numberOfCores',
                           '_AtomicCoordinationNumberConstraint__shellsIndexes',
                           '_AtomicCoordinationNumberConstraint__lowerShells',
                           '_AtomicCoordinationNumberConstraint__upperShells',
                           '_AtomicCoordinationNumberConstraint__minAtoms',
                           '_AtomicCoordinationNumberConstraint__maxAtoms',
                           '_AtomicCoordinationNumberConstraint__coordNumData',
                           '_AtomicCoordinationNumberConstraint__weights',
                           '_AtomicCoordinationNumberConstraint__asCoreDefIdxs',
                           '_AtomicCoordinationNumberConstraint__inShellDefIdxs',] )
        RUNTIME_DATA = [d for d in self.RUNTIME_DATA]
        RUNTIME_DATA.extend( ['_AtomicCoordinationNumberConstraint__coordNumData',
                              '_AtomicCoordinationNumberConstraint__coresIndexes',
                              '_AtomicCoordinationNumberConstraint__shellsIndexes',
                              '_AtomicCoordinationNumberConstraint__asCoreDefIdxs',
                              '_AtomicCoordinationNumberConstraint__inShellDefIdxs'] )
        object.__setattr__(self, 'FRAME_DATA',   tuple(FRAME_DATA)   )
        object.__setattr__(self, 'RUNTIME_DATA', tuple(RUNTIME_DATA) )

    def _codify_update__(self, name='constraint', addDependencies=True):
        dependencies = []
        code         = []
        if addDependencies:
            code.extend(dependencies)
        code.append("{name}.set_used({val})".format(name=name, val=self.used))
        code.append("{name}.set_reject_probability({val})".format(name=name, val=self.rejectProbability))
        code.append("{name}.set_coordination_number_definition({val})".format(name=name, val=self.__coordNumDef))
        # return
        return dependencies, '\n'.join(code)

    def _codify__(self, engine, name='constraint', addDependencies=True):
        assert isinstance(name, basestring), LOGGER.error("name must be a string")
        assert re.match('[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None, LOGGER.error("given name '%s' can't be used as a variable name"%name)
        dependencies = 'from fullrmc.Constraints import AtomicCoordinationConstraints'
        code         = []
        if addDependencies:
            code.append(dependencies)
        code.append("{name} = AtomicCoordinationConstraints.AtomicCoordinationNumberConstraint\
(rejectProbability={rejectProbability})".format(name=name, rejectProbability=self.rejectProbability))
        code.append("{engine}.add_constraints([{name}])".format(engine=engine, name=name))
        if self.__coordNumDef is not None:
            code.append("{name}.set_coordination_number_definition({coordDef})".
            format(name=name, coordDef=self.__coordNumDef))
        # return
        return [dependencies], '\n'.join(code)

    def __initialize_constraint_data(self):
        # set definition
        self.__coordNumDef = None
        # the following is the parsing of defined shells
        self.__coresIndexes  = []
        self.__numberOfCores = []
        self.__shellsIndexes = []
        self.__lowerShells   = []
        self.__upperShells   = []
        self.__minAtoms      = []
        self.__maxAtoms      = []
        # upon computing constraint data, those values must be divided by len( self.__coresIndexes[i] )
        self.__coordNumData = []
        self.__weights      = []
        # atoms to cores and shells pointers
        self.__asCoreDefIdxs  = []
        self.__inShellDefIdxs = []
        # no need to dump to repository because all of those attributes will be written
        # at the point of setting the definition.

    def _on_collector_reset(self):
        pass

    @property
    def coordNumDef(self):
        """Copy of coordination number definition dictionary"""
        return self.coordinationNumberDefinition

    @property
    def coordinationNumberDefinition(self):
        """alias to coordinationNumberDefinition"""
        return copy.deepcopy( self.__coordNumDef )

    @property
    def coresIndexes(self):
        """List of coordination number core atoms index array."""
        return self.__coresIndexes

    @property
    def shellsIndexes(self):
        """List of coordination number shell atoms index array."""
        return self.__shellsIndexes

    @property
    def numberOfCores(self):
        """Array of number of core atoms"""
        return self.__numberOfCores

    @property
    def lowerShells(self):
        """Array of lower shells distance."""
        return self.__lowerShells

    @property
    def upperShells(self):
        """Array of upper shells distance. """
        return self.__upperShells

    @property
    def minAtoms(self):
        """Array of minimum number of atoms in a shell."""
        return self.__minAtoms

    @property
    def maxAtoms(self):
        """Array of maximum number of atoms in a shell. """
        return self.__maxAtoms

    @property
    def weights(self):
        """Shells weight which count in the computation of standard error."""
        return self.__weights

    @property
    def data(self):
        """Coordination number constraint data."""
        return self.__coordNumData

    @property
    def asCoreDefIdxs(self):
        """List of arrays where each element is pointing to a coordination
        number definition where the atom is a core."""
        return self.__asCoreDefIdxs

    @property
    def inShellDefIdxs(self):
        """List of arrays where each element is pointing to a coordination
        number definition where the atom is in a shell."""
        return self.__inShellDefIdxs

    def listen(self, message, argument=None):
        """
        listen to any message sent from the Broadcaster.

        :Parameters:
            #. message (object): Any python object to send to constraint's
               listen method.
            #. argument (object): Any type of argument to pass to the listeners.
        """
        if message in ("engine set","update pdb","update molecules indexes","update elements indexes","update names indexes"):
            self.set_coordination_number_definition(self.__coordNumDef)
            # reset constraint is called in set_coordination_number_definition
        elif message in("update boundary conditions",):
            self.reset_constraint()

    #@raise_if_collected
    def set_coordination_number_definition(self, coordNumDef):
        """
        Set the coordination number definition.

        :Parameters:
            #. coordNumDef (None, list, tuple): Coordination number definition.
               It must be None, list or tuple where every element is a list or
               a tuple of exactly 6 items and an optional 7th item for weight.

               #. core atoms: Can be any of the following:

                  * string: indicating atomic element.
                  * dictionary: Key as atomic attribute among (element, name)
                    and value is the attribute value.
                  * list, tuple, set, numpy.ndarray: core atoms index.

               #. in shell atoms: Can be any of the following:

                  * string: indicating atomic element.
                  * dictionary: Key as atomic attribute among (element, name)
                    and value is the attribute value.
                  * list, tuple, set, numpy.ndarray: in shell atoms index

               #. Lower distance limit of the coordination shell.
               #. Upper distance limit of the coordination shell.
               #. :math:`N_{min}` : minimum number of neighbours in the
                  shell.
               #. :math:`N_{max}` : maximum number of neighbours in the
                  shell.
               #. :math:`W_{i}` : weight contribution to the standard error,
                  this is optional, if not given it is set automatically to 1.0.

               ::

                   e.g. [ ('Ti','Ti', 2.5, 3.5, 5, 7.1, 1), ('Ni','Ti', 2.2, 3.1, 7.2, 9.7, 100), ...]
                        [ ({'element':'Ti'},'Ti', 2.5, 3.5, 5, 7.1, 0.1), ...]
                        [ ({'name':'au'},'Au', 2.5, 3.5, 4.1, 6.3), ...]
                        [ ({'name':'Ni'},{'element':'Ti'}, 2.2, 3.1, 7, 9), ...]
                        [ ('Ti',range(100,500), 2.2, 3.1, 7, 9), ...]
                        [ ([0,10,11,15,1000],{'name':'Ti'}, 2.2, 3.1, 7, 9, 5), ...]

        """
        if self.engine is None:
            self.__coordNumDef = coordNumDef
            return
        elif coordNumDef is None:
            coordNumDef = []
        ########## check definitions, create coordination number data ##########
        self.__initialize_constraint_data()
        ALL_NAMES       = self.engine.get_original_data("allNames")
        NAMES           = self.engine.get_original_data("names")
        ALL_ELEMENTS    = self.engine.get_original_data("allElements")
        ELEMENTS        = self.engine.get_original_data("elements")
        NUMBER_OF_ATOMS = self.engine.get_original_data("numberOfAtoms")
        for CNDef in coordNumDef:
            assert isinstance(CNDef, (list, tuple)), LOGGER.error("coordNumDef item must be a list or a tuple")
            if len(CNDef) == 6:
                coreDef, shellDef, lowerShell, upperShell, minCN, maxCN = CNDef
                weight = 1.0
            elif len(CNDef) == 7:
                coreDef, shellDef, lowerShell, upperShell, minCN, maxCN, weight = CNDef
            else:
                raise LOGGER.error("coordNumDef item must have 6 or 7 items")
            # core definition
            if isinstance(coreDef, basestring):
                coreDef = str(coreDef)
                assert coreDef in ELEMENTS, LOGGER.error("core atom definition '%s' is not a valid element"%coreDef)
                coreIndexes = [idx for idx, el in enumerate(ALL_ELEMENTS) if el==coreDef]
            elif isinstance(coreDef, dict):
                assert len(coreDef) == 1, LOGGER.error("core atom definition dictionary must be of length 1")
                key, value = list(coreDef)[0], list(coreDef.values())[0]
                if key is "name":
                    assert value in NAMES, LOGGER.error("core atom definition '%s' is not a valid name"%coreDef)
                    coreIndexes = [idx for idx, el in enumerate(ALL_NAMES) if el==coreDef]
                elif key is "element":
                    assert value in ELEMENTS, LOGGER.error("core atom definition '%s' is not a valid element"%coreDef)
                    coreIndexes = [idx for idx, el in enumerate(ALL_ELEMENTS) if el==coreDef]
                else:
                    raise LOGGER.error("core atom definition dictionary key must be either 'name' or 'element'")
            elif isinstance(coreDef, (list, tuple, set, np.ndarray)):
                coreIndexes = []
                if isinstance(coreDef, np.ndarray):
                    assert len(coreDef.shape)==1, LOGGER.error("core atom definition numpy.ndarray must be 1D")
                for c in coreDef:
                    assert is_integer(c), LOGGER.error("core atom definition index must be integer")
                    c = INT_TYPE(c)
                    assert c>=0, LOGGER.error("core atom definition index must be >=0")
                    assert c<NUMBER_OF_ATOMS, LOGGER.error("core atom definition index must be smaler than number of atoms in system")
                    coreIndexes.append(c)
            # shell definition
            if isinstance(shellDef, basestring):
                shellDef = str(shellDef)
                assert shellDef in ELEMENTS, LOGGER.error("core atom definition '%s' is not a valid element"%shellDef)
                shellIndexes = [idx for idx, el in enumerate(ALL_ELEMENTS) if el==shellDef]
            elif isinstance(shellDef, dict):
                assert len(shellDef) == 1, LOGGER.error("core atom definition dictionary must be of length 1")
                key, value = list(shellDef)[0], list(shellDef.values())[0]
                if key is "name":
                    assert value in NAMES, LOGGER.error("core atom definition '%s' is not a valid name"%shellDef)
                    shellIndexes = [idx for idx, el in enumerate(ALL_NAMES) if el==shellDef]
                elif key is "element":
                    assert value in ELEMENTS, LOGGER.error("core atom definition '%s' is not a valid element"%shellDef)
                    shellIndexes = [idx for idx, el in enumerate(ALL_ELEMENTS) if el==shellDef]
                else:
                    raise LOGGER.error("core atom definition dictionary key must be either 'name' or 'element'")
            elif isinstance(shellDef, (list, tuple, set, np.ndarray)):
                shellIndexes = []
                if isinstance(shellDef, np.ndarray):
                    assert len(shellDef.shape)==1, LOGGER.error("core atom definition numpy.ndarray must be 1D")
                for c in shellDef:
                    assert is_integer(c), LOGGER.error("core atom definition index must be integer")
                    c = INT_TYPE(c)
                    assert c>=0, LOGGER.error("core atom definition index must be >=0")
                    assert c<NUMBER_OF_ATOMS, LOGGER.error("core atom definition index must be smaler than number of atoms in system")
                    shellIndexes.append(c)
            # lower and upper shells definition
            assert is_number(lowerShell), LOGGER.error("Coordination number lower shell '%s' must be a number."%lowerShell)
            lowerShell = FLOAT_TYPE(lowerShell)
            assert lowerShell>=0, LOGGER.error("Coordination number lower shell '%s' must be a positive."%lowerShell)
            assert is_number(upperShell), LOGGER.error("Coordination number upper shell '%s' must be a number."%key)
            upperShell = FLOAT_TYPE(upperShell)
            assert upperShell>lowerShell, LOGGER.error("Coordination number lower shell '%s' must be smaller than upper shell %s"%(lowerShell,upperShell))
            # minimum and maximum number of atoms definitions
            assert is_number(minCN), LOGGER.error("Coordination number minimum atoms '%s' must be a number."%minCN)
            minCN = FLOAT_TYPE(minCN)
            assert minCN>=0, LOGGER.error("Coordination number minimim atoms '%s' must be >=0."%minCN)
            assert is_number(maxCN), LOGGER.error("Coordination number maximum atoms '%s' must be a number."%key)
            maxCN = FLOAT_TYPE(maxCN)
            assert maxCN>=minCN, LOGGER.error("Coordination number minimum atoms '%s' must be smaller than maximum atoms %s"%(minCN,maxCN))
            # check weight
            assert is_number(weight), LOGGER.error("Coordination number weight '%s' must be a number."%weight)
            weight = FLOAT_TYPE(weight)
            assert weight>0, LOGGER.error("Coordination number weight '%s' must be >0."%weight)
            # append coordination number data
            self.__coresIndexes.append( sorted(set(coreIndexes)) )
            self.__shellsIndexes.append( sorted(set(shellIndexes)) )
            self.__lowerShells.append( lowerShell )
            self.__upperShells.append( upperShell )
            self.__minAtoms.append( minCN )
            self.__maxAtoms.append( maxCN )
            #self.__coordNumData.append( FLOAT_TYPE(0) )
            self.__coordNumData.append( None )
            self.__weights.append( weight )
        ########## set asCoreDefIdxs and inShellDefIdxs points ##########
        for _ in xrange(NUMBER_OF_ATOMS):
            self.__asCoreDefIdxs.append( [] )
            self.__inShellDefIdxs.append( [] )
        for defIdx, indexes in enumerate(self.__coresIndexes):
            self.__coresIndexes[defIdx] = np.array( indexes, dtype=INT_TYPE )
            for atIdx in indexes:
                self.__asCoreDefIdxs[atIdx].append( defIdx )
        for defIdx, indexes in enumerate(self.__shellsIndexes):
            self.__shellsIndexes[defIdx] = np.array( indexes, dtype=INT_TYPE )
            for atIdx in indexes:
                self.__inShellDefIdxs[atIdx].append( defIdx )
        for atIdx in xrange(NUMBER_OF_ATOMS):
            self.__asCoreDefIdxs[atIdx]  = np.array( self.__asCoreDefIdxs[atIdx], dtype=INT_TYPE )
            self.__inShellDefIdxs[atIdx] = np.array( self.__inShellDefIdxs[atIdx], dtype=INT_TYPE )
        # set all to arrays
        #self.__coordNumData  = np.array( self.__coordNumData, dtype=FLOAT_TYPE )
        self.__weights       = np.array( self.__weights, dtype=FLOAT_TYPE )
        self.__numberOfCores = np.array( [len(idxs) for idxs in self.__coresIndexes], dtype=FLOAT_TYPE )
        # set definition
        self.__coordNumDef = coordNumDef
        # dump to repository
        self._dump_to_repository({'_AtomicCoordinationNumberConstraint__coordNumDef'   :self.__coordNumDef,
                                  '_AtomicCoordinationNumberConstraint__coordNumData'  :self.__coordNumData,
                                  '_AtomicCoordinationNumberConstraint__asCoreDefIdxs' :self.__asCoreDefIdxs,
                                  '_AtomicCoordinationNumberConstraint__inShellDefIdxs':self.__inShellDefIdxs,
                                  '_AtomicCoordinationNumberConstraint__weights'       :self.__weights,
                                  '_AtomicCoordinationNumberConstraint__numberOfCores' :self.__numberOfCores,
                                  '_AtomicCoordinationNumberConstraint__coresIndexes'  :self.__coresIndexes,
                                  '_AtomicCoordinationNumberConstraint__shellsIndexes' :self.__shellsIndexes,
                                  '_AtomicCoordinationNumberConstraint__lowerShells'   :self.__lowerShells,
                                  '_AtomicCoordinationNumberConstraint__upperShells'   :self.__upperShells,
                                  '_AtomicCoordinationNumberConstraint__minAtoms'      :self.__minAtoms,
                                  '_AtomicCoordinationNumberConstraint__maxAtoms'      :self.__maxAtoms})
        # reset constraint
        self.reset_constraint() # ADDED 2017-JAN-08

    def compute_standard_error(self, data):
        """
        Compute the standard error (StdErr) of data not satisfying constraint's
        conditions.

        .. math::
            StdErr = \\sum \\limits_{i}^{S} Dev_{i}


        .. math::
            Dev_{i}=\\begin{cases}
              W_{i}*( N_{min,i}-\\overline{CN_{i}} ), & \\text{if $\\overline{CN_{i}}<N_{min,i}$}.\\\\
              W_{i}*( \\overline{CN_{i}}-N_{max,i} ), & \\text{if $\\overline{CN_{i}}>N_{max,i}$}.\\\\
              0                  , & \\text{if $N_{min,i}<=\\overline{CN_{i}}<=N_{max,i}$}
            \\end{cases}


        Where:\n
        :math:`S`                  is the total number of defined coordination number shells. \n
        :math:`W_{i}`              is the defined weight of coordination number shell i. \n
        :math:`Dev_{i}`            is the standard deviation of the coordination number in shell definition i. \n
        :math:`\\overline{CN_{i}}` is the mean coordination number value in shell definition i. \n
        :math:`N_{min,i}`          is the defined minimum number of neighbours in shell definition i. \n
        :math:`N_{max,i}`          is the defined maximum number of neighbours in shell definition i. \n


        :Parameters:
            #. data (numpy.array): The constraint value data to compute
               standardError.

        :Returns:
            #. standardError (number): The calculated standardError of the
               constraint.
        """
        coordNum = data/self.__numberOfCores
        StdErr   = 0.
        for idx, cn in enumerate( coordNum ):
            if cn < self.__minAtoms[idx]:
                StdErr += self.__weights[idx]*(self.__minAtoms[idx]-cn)
            elif cn > self.__maxAtoms[idx]:
                StdErr += self.__weights[idx]*(cn-self.__maxAtoms[idx])
        return StdErr

    # THIS NEEDS TO BE FORMATTED HUMAN READABLE RETURN 2017-07-29
    def get_constraint_value(self):
        """
        Get constraint's data.

        :Returns:
            #. data (numpy.array): The constraint value data
        """
        return self.data

    @reset_if_collected_out_of_date
    def compute_data(self, update=True):
        """ Compute constraint's data.

        :Parameters:
            #. update (boolean): whether to update constraint data and
               standard error with new computation. If data is computed and
               updated by another thread or process while the stochastic
               engine is running, this might lead to a state alteration of
               the constraint which will lead to a no additional accepted
               moves in the run

        :Returns:
            #. data (dict): constraint data dictionary
            #. standardError (float): constraint standard error
        """
        coordNumData = np.array( [FLOAT_TYPE(0) for _ in self.__coordNumData], dtype=FLOAT_TYPE )
        all_atoms_coord_number_coords(boxCoords      = self.engine.boxCoordinates,
                                      basis          = self.engine.basisVectors,
                                      isPBC          = self.engine.isPBC,
                                      coresIndexes   = self.__coresIndexes,
                                      shellsIndexes  = self.__shellsIndexes,
                                      lowerShells    = self.__lowerShells,
                                      upperShells    = self.__upperShells,
                                      asCoreDefIdxs  = self.__asCoreDefIdxs,
                                      inShellDefIdxs = self.__inShellDefIdxs,
                                      coordNumData   = coordNumData,
                                      ncores         = self.engine._runtime_ncores)
        # create data and compute standard error
        coordNumData /= FLOAT_TYPE(2.)
        stdError      = self.compute_standard_error(data = coordNumData)
        # update
        if update:
            self.__coordNumData = coordNumData
            self.set_data( coordNumData )
            self.set_active_atoms_data_before_move(None)
            self.set_active_atoms_data_after_move(None)
            # set standardError
            self.set_standard_error(stdError)
            # set original data
            if self.originalData is None:
                self._set_original_data(self.data)
        # return
        return coordNumData, stdError

    def compute_before_move(self, realIndexes, relativeIndexes):
        """
        Compute constraint's data before move is executed.

        :Parameters:
            #. realIndexes (numpy.ndarray): Not used here.
            #. relativeIndexes (numpy.ndarray): Group atoms relative index
               the move will be applied to.
        """
        beforeMoveData = np.zeros(self.__coordNumData.shape, dtype=self.__coordNumData.dtype)
        multi_atoms_coord_number_coords( indexes        = relativeIndexes,
                                         boxCoords      = self.engine.boxCoordinates,
                                         basis          = self.engine.basisVectors,
                                         isPBC          = self.engine.isPBC,
                                         coresIndexes   = self.__coresIndexes,
                                         shellsIndexes  = self.__shellsIndexes,
                                         lowerShells    = self.__lowerShells,
                                         upperShells    = self.__upperShells,
                                         asCoreDefIdxs  = self.__asCoreDefIdxs,
                                         inShellDefIdxs = self.__inShellDefIdxs,
                                         coordNumData   = beforeMoveData,
                                         ncores         = self.engine._runtime_ncores)
        # set active atoms data before move
        self.set_active_atoms_data_before_move( beforeMoveData )
        self.set_active_atoms_data_after_move(None)

    def compute_after_move(self, realIndexes, relativeIndexes, movedBoxCoordinates):
        """
        Compute constraint's data after move is executed.

        :Parameters:
            #. realIndexes (numpy.ndarray): Not used here.
            #. relativeIndexes (numpy.ndarray): Group atoms relative index
               the move will be applied to.
            #. movedBoxCoordinates (numpy.ndarray): The moved atoms new coordinates.
        """
        # change coordinates temporarily
        boxData = np.array(self.engine.boxCoordinates[relativeIndexes], dtype=FLOAT_TYPE)
        self.engine.boxCoordinates[relativeIndexes] = movedBoxCoordinates
        # compute after move data
        afterMoveData = np.zeros(self.__coordNumData.shape, dtype=self.__coordNumData.dtype)
        multi_atoms_coord_number_coords( indexes        = relativeIndexes,
                                         boxCoords      = self.engine.boxCoordinates,
                                         basis          = self.engine.basisVectors,
                                         isPBC          = self.engine.isPBC,
                                         coresIndexes   = self.__coresIndexes,
                                         shellsIndexes  = self.__shellsIndexes,
                                         lowerShells    = self.__lowerShells,
                                         upperShells    = self.__upperShells,
                                         asCoreDefIdxs  = self.__asCoreDefIdxs,
                                         inShellDefIdxs = self.__inShellDefIdxs,
                                         coordNumData   = afterMoveData,
                                         ncores         = self.engine._runtime_ncores)
        # reset coordinates
        self.engine.boxCoordinates[relativeIndexes] = boxData
        # set active atoms data after move
        self.set_active_atoms_data_after_move( afterMoveData )
        # compute after move standard error
        self.__coordNumDataAfterMove = self.__coordNumData-self.activeAtomsDataBeforeMove+self.activeAtomsDataAfterMove
        self.set_after_move_standard_error( self.compute_standard_error(data = self.__coordNumDataAfterMove) )
        # increment tried
        self.increment_tried()

    def accept_move(self, realIndexes, relativeIndexes):
        """
        Accept move.

        :Parameters:
            #. realIndexes (numpy.ndarray): not used here.
            #. relativeIndexes (numpy.ndarray): Not used here.
        """
        self.__coordNumData = self.__coordNumDataAfterMove
        self.set_data( self.__coordNumData ) # ADDED LATER 2016-11-27 to be verified.
        # reset activeAtoms data
        self.set_active_atoms_data_before_move(None)
        self.set_active_atoms_data_after_move(None)
        # update standardError
        self.set_standard_error(self.afterMoveStandardError)
        self.set_after_move_standard_error( None )
        # increment accepted
        self.increment_accepted()

    def reject_move(self, realIndexes, relativeIndexes):
        """
        Reject move.

        :Parameters:
            #. realIndexes (numpy.ndarray): not used here.
            #. relativeIndexes (numpy.ndarray): Not used here.
        """
        # reset activeAtoms data
        self.set_active_atoms_data_before_move(None)
        self.set_active_atoms_data_after_move(None)
        # update standardError
        self.set_after_move_standard_error( None )

    def compute_as_if_amputated(self, realIndex, relativeIndex):
        """
        Compute and return constraint's data and standard error as if atom given its
        its was amputated.

        :Parameters:
            #. realIndex (numpy.ndarray): Not used here.
            #. relativeIndex (numpy.ndarray): Not used here.
        """
        pass

    def accept_amputation(self, realIndex, relativeIndex):
        """
        Accept amputation of atom and sets constraints data and standard error accordingly.

        :Parameters:
            #. realIndex (numpy.ndarray): Atom's index as a numpy array
               of a single element.
            #. relativeIndex (numpy.ndarray): Atom's relative index as a numpy
               array of a single element.
        """
        # MAYBE WE DON"T NEED TO CHANGE DATA AND SE. BECAUSE THIS MIGHT BE A PROBLEM
        # WHEN IMPLEMENTING ATOMS RELEASING. MAYBE WE NEED TO COLLECT DATA INSTEAD, REMOVE
        # AND ADD UPON RELEASE
        self.compute_before_move(realIndexes=realIndex, relativeIndexes=relativeIndex )
        #self.compute_before_move(indexes = np.array([index], dtype=INT_TYPE) )
        # change permanently data attribute
        self.__coordNumData = self.__coordNumData-self.activeAtomsDataBeforeMove
        self.set_data( self.__coordNumData )
        self.set_active_atoms_data_before_move(None)
        self.set_standard_error( self.compute_standard_error(data = self.__coordNumData) )

    def reject_amputation(self, realIndex, relativeIndex):
        """
        Reject amputation of atom.

        :Parameters:
            #. realIndex (numpy.ndarray): Not used here.
            #. relativeIndex (numpy.ndarray): Not used here
        """
        pass

    def _on_collector_collect_atom(self, realIndex):
        # get relative index
        relativeIndex = self._atomsCollector.get_relative_index(realIndex)
        # create data dict
        dataDict = {}
        # cores indexes
        coresIndexes = []
        for idx, ci in enumerate(self.__coresIndexes):
            coresIndexes.append( np.where(ci==relativeIndex)[0] )
            ci = np.delete(ci, coresIndexes[-1], axis=0)
            ci[np.where(ci>relativeIndex)[0]] -= 1
            self.__coresIndexes[idx] = ci
        dataDict['coresIndexes'] = coresIndexes
        # shells indexes
        shellsIndexes = []
        for idx, si in enumerate(self.__shellsIndexes):
            shellsIndexes.append( np.where(si==relativeIndex)[0] )
            si = np.delete(si, shellsIndexes[-1], axis=0)
            si[np.where(si>relativeIndex)[0]] -= 1
            self.__shellsIndexes[idx] = si
        dataDict['shellsIndexes'] = shellsIndexes
        # asCorDefIdxs and inShellDefIdxs
        dataDict['asCoreDefIdxs']  = self.__asCoreDefIdxs.pop(relativeIndex)
        dataDict['inShellDefIdxs'] = self.__inShellDefIdxs.pop(relativeIndex)
        # correct number of cores without collecting
        for idx, ci in enumerate(coresIndexes):
            self.__numberOfCores[idx] -= len(ci)
        # collect atom
        self._atomsCollector.collect(realIndex, dataDict=dataDict)

    def _on_collector_release_atom(self, realIndex):
        pass

    def _plot(self, frameIndex, propertiesLUT,
                    # plotting arguments
                    ax, dataParams, barParams, txtParams,
                    xlabelParams, ylabelParams,
                    xticksParams,yticksParams,
                    legendParams, titleParams, *args, **kwargs):
        # get needed data
        frame                = propertiesLUT['frames-name'][frameIndex]
        data                 = propertiesLUT['frames-data'][frameIndex]
        standardError        = propertiesLUT['frames-standard_error'][frameIndex]
        numberOfRemovedAtoms = propertiesLUT['frames-number_of_removed_atoms'][frameIndex]
        # import matplotlib
        import matplotlib.pyplot as plt
        # plot bars
        barParams = copy.deepcopy(barParams)
        width  = barParams.pop('width', 0.6)
        ind    = np.arange(1,len(data)+1)  # the x locations for the groups
        if not len(self.minAtoms):
            LOGGER.warn("@{frm} no coordination shells found. It's even not defined or no atoms where found in definition.".format(frm=frame))
            return
        bottom = self.minAtoms
        height = [self.maxAtoms[idx]-self.minAtoms[idx] for idx in xrange(len(self.maxAtoms))]
        p = ax.bar(ind+width/2., height, width, bottom=self.minAtoms, **barParams)
        # add coordination number points
        CN = data/self.__numberOfCores
        ax.plot(ind+width/2., CN,  **dataParams)
        # set ticks
        ax.set_xticks(ind+width/2.)
        ax.set_xticklabels(["%s-%s"%(e[:2]) for e in self.__coordNumDef], **xticksParams)
        # compute standard errors
        if txtParams is not None:
            stdErrs  = []
            for idx, cn in enumerate( CN ):
                if cn < self.__minAtoms[idx]:
                    stdErrs.append( self.__weights[idx]*(self.__minAtoms[idx]-cn) )
                elif cn > self.__maxAtoms[idx]:
                    stdErrs.append( self.__weights[idx]*(cn-self.__maxAtoms[idx]) )
                else:
                    stdErrs.append( 0. )
            for mi,ma, std, rect in zip(self.__minAtoms,self.__maxAtoms,stdErrs, ax.patches):
                height = rect.get_height()
                t = ax.text(x     = rect.get_x() + rect.get_width()/2,
                              y     = float(ma+mi)/2.,
                              s     = " "+str(std),
                              **txtParams)
        # set limits
        minY = min([min(CN),min(self.minAtoms)])
        maxY = max([max(CN),max(self.maxAtoms)])
        ax.set_xlim(0,len(data)+1.5)
        ax.set_ylim(minY-1,maxY+1)
        # plot legend
        if legendParams is not None:
            ax.legend(**legendParams)
        # set axis labels
        ax.set_xlabel(**xlabelParams)
        ax.set_ylabel(**ylabelParams)
        # set title
        if titleParams is not None:
            title = copy.deepcopy(titleParams)
            label = title.pop('label',"").format(frame=frame,standardError=standardError, numberOfRemovedAtoms=numberOfRemovedAtoms,used=self.used)
            ax.set_title(label=label, **title)

    def plot(self, dataParams  = {'label':'mean coord num', 'marker':'o', 'linewidth':0, 'color':'#ffcc00','markersize':20, 'markevery':1},
                   barParams   = {'label':"boundaries", 'color':'#99ccff', 'width':0.6},
                   txtParams   = {'color':'black', 'fontsize':8, 'rotation':90, 'horizontalalignment':'center', 'verticalalignment':'center'},
                   xlabelParams={'xlabel':'Core-Shell atoms', 'size':10},
                   ylabelParams={'ylabel':'Coordination number', 'size':10},
                   xticksParams={'fontsize': 8, 'rotation':45},
                   titleParams = {'label':"@{frame} (${numberOfRemovedAtoms:.1f}$ $rem.$ $at.$) $Std.Err.={standardError:.3f}$", "fontsize":8},
                   **kwargs):
        """
        Alias to Constraint.plot with additional parameters

        :Additional/Adjusted Parameters:
            #. dataParams (None, dict): modified constraint data plotting parameters
            #. barParams (None, dict): matplotlib.axes.Axes.bar parameters
            #. txtParams (None, dict): matplotlib.axes.Axes.text parameters
            #. xlabelParams (None, dict): modified matplotlib.axes.Axes.set_xlabel
               parameters.
            #. ylabelParams (None, dict): modified matplotlib.axes.Axes.set_ylabel
               parameters.
            #. xticksParams (None, dict): modified matplotlib.axes.Axes.set_xticklabels
               parameters.
            #. titleParams (None, dict): title format.
            #. show (boolean): Whether to render and show figure before
               returning.
        """
        return super(AtomicCoordinationNumberConstraint, self).plot(dataParams  = dataParams,
                                                                    barParams   = barParams,
                                                                    txtParams   = txtParams,
                                                                    xlabelParams= xlabelParams,
                                                                    ylabelParams= ylabelParams,
                                                                    xticksParams= xticksParams,
                                                                    titleParams = titleParams,
                                                                    **kwargs)


    def _get_export(self, frameIndex, propertiesLUT, format='%s'):
        # create data, metadata and header
        data = propertiesLUT['frames-data'][frameIndex]
        # get numbers and differences
        CN      = data/self.__numberOfCores
        stdErrs = []
        for idx, cn in enumerate( CN ):
            if cn < self.__minAtoms[idx]:
                stdErrs.append( self.__weights[idx]*(self.__minAtoms[idx]-cn) )
            elif cn > self.__maxAtoms[idx]:
                stdErrs.append( self.__weights[idx]*(cn-self.__maxAtoms[idx]) )
            else:
                stdErrs.append( 0. )
        # start creating header and data
        header = ["core-shell","ninimum_coord_num","naximum_coord_num","mean_coord_num","standard_error"]
        # create data
        data = []
        for i,e in enumerate(self.__coordNumDef):
            data.append( ["%s-%s"%(e[:2]),
                          str(self.__maxAtoms[i]),
                          str(self.__maxAtoms[i]),
                          str(CN[i]),
                          format%(stdErrs[i],)] )
        # return
        return header, data



    def _constraint_copy_needs_lut(self):
        return {'_AtomicCoordinationNumberConstraint__coresIndexes'  :'_AtomicCoordinationNumberConstraint__coresIndexes',
                '_AtomicCoordinationNumberConstraint__shellsIndexes' :'_AtomicCoordinationNumberConstraint__shellsIndexes',
                '_AtomicCoordinationNumberConstraint__lowerShells'   :'_AtomicCoordinationNumberConstraint__lowerShells',
                '_AtomicCoordinationNumberConstraint__upperShells'   :'_AtomicCoordinationNumberConstraint__upperShells',
                '_AtomicCoordinationNumberConstraint__asCoreDefIdxs' :'_AtomicCoordinationNumberConstraint__asCoreDefIdxs',
                '_AtomicCoordinationNumberConstraint__inShellDefIdxs':'_AtomicCoordinationNumberConstraint__inShellDefIdxs',
                '_AtomicCoordinationNumberConstraint__minAtoms'      :'_AtomicCoordinationNumberConstraint__minAtoms',
                '_AtomicCoordinationNumberConstraint__maxAtoms'      :'_AtomicCoordinationNumberConstraint__maxAtoms',
                '_AtomicCoordinationNumberConstraint__weights'       :'_AtomicCoordinationNumberConstraint__weights',
                '_AtomicCoordinationNumberConstraint__numberOfCores' :'_AtomicCoordinationNumberConstraint__numberOfCores',
                '_AtomicCoordinationNumberConstraint__coordNumDef'   :'_AtomicCoordinationNumberConstraint__coordNumDef',
                '_AtomicCoordinationNumberConstraint__coordNumData'  :'_AtomicCoordinationNumberConstraint__coordNumData',
                '_Constraint__used'                                  :'_Constraint__used',
                '_Constraint__data'                                  :'_Constraint__data',
                '_Constraint__standardError'                         :'_Constraint__standardError',
                '_Constraint__state'                                 :'_Constraint__state',
                '_Engine__state'                                     :'_Engine__state',
                '_Engine__boxCoordinates'                            :'_Engine__boxCoordinates',
                '_Engine__basisVectors'                              :'_Engine__basisVectors',
                '_Engine__isPBC'                                     :'_Engine__isPBC',
                '_Engine__moleculesIndex'                            :'_Engine__moleculesIndex',
                '_Engine__elementsIndex'                             :'_Engine__elementsIndex',
                '_Engine__numberOfAtomsPerElement'                   :'_Engine__numberOfAtomsPerElement',
                '_Engine__elements'                                  :'_Engine__elements',
                '_Engine__numberDensity'                             :'_Engine__numberDensity',
                '_Engine__volume'                                    :'_Engine__volume',
                '_atomsCollector'                                    :'_atomsCollector',
                ('engine','_atomsCollector')                         :'_atomsCollector',
               }

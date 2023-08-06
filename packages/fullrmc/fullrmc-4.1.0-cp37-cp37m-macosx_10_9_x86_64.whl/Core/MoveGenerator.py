"""
MoveGenerator contains parent classes for all move generators.
A MoveGenerator sub-class is used at fullrmc's stochastic engine runtime to
generate moves upon selected groups.
Every group has its own MoveGenerator class and definitions, therefore it is
possible to fully customize how a group of atoms should move.

.. inheritance-diagram:: fullrmc.Core.MoveGenerator
    :parts: 1
"""
# standard libraries imports
from __future__ import print_function
import collections, inspect, re
from random import randint, shuffle

# external libraries imports
import numpy as np

# fullrmc imports
from ..Globals import INT_TYPE, FLOAT_TYPE, LOGGER
from ..Globals import str, long, unicode, bytes, basestring, range, xrange, maxint
from ..Core.Collection import ListenerBase, is_number, is_integer, get_path, generate_random_float
from ..Core.Collection import _Container


#class MoveGenerator(ListenerBase):
class MoveGenerator(object):
    """
    It is the parent class of all moves generators.
    This class can't be instantiated but its sub-classes might be.

    :Parameters:
        #. group (None, Group): The group instance.
    """
    def __init__(self, group=None):
        # init ListenerBase
        super(MoveGenerator, self).__init__()
        # set group
        self.set_group(group)

    def _codify__(self, *args, **kwargs):
        raise Exception(LOGGER.impl("'%s' method must be overloaded"%inspect.stack()[0][3]))

    @property
    def group(self):
        """ Group instance."""
        return self.__group

    def set_group(self, group):
        """
        Set the MoveGenerator group.

        :Parameters:
            #. group (None, Group): Group instance.
        """
        if group is not None:
            from fullrmc.Core.Group import Group
            assert isinstance(group, Group), LOGGER.error("group must be a fullrmc Group instance")
            valid, message = self.check_group(group)
            if not valid:
                raise Exception( LOGGER.error("%s"%message) )
        self.__group = group

    def check_group(self, group):
        """
        Check the generator's group.
        This method must be overloaded in all MoveGenerator sub-classes.

        :Parameters:
            #. group (Group): the Group instance
        """
        raise Exception(LOGGER.impl("MovesGenerator '%s' method must be overloaded"%inspect.stack()[0][3]))

    def transform_coordinates(self, coordinates, argument=None):
        """
        Transform coordinates. This method is called to move atoms.
        This method must be overloaded in all MoveGenerator sub-classes.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the move.
            #. argument (object): Any other argument needed to perform the
               move. In General it's not needed.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after applying
               the move.
        """
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def move(self, coordinates):
        """
        Moves coordinates.
        This method must NOT be overloaded in MoveGenerator sub-classes.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the transformation.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after applying
               the transformation.
        """
        return self.transform_coordinates(coordinates=coordinates)


class RemoveGenerator(MoveGenerator):
    """
    This is a very particular move generator that will not generate moves on
    atoms but removes them from the atomic configuration using a general
    collector mechanism. Remove generators must be used to create defects in
    the simulated system. When the standard error is high, removing atoms
    might reduce the total fit standard error but this can be illusional and
    very limiting because artificial non physical voids can get created in
    the system which will lead to an impossibility to finding a solution at
    the end. It's strongly recommended to exhaust all ideas and possibilities
    in finding a good solution prior to start removing atoms unless structural
    defects is the goal of the simulation.\n
    All removed or amputated atoms are collected by the engine and will
    become available to be re-inserted in the system if needed. But keep in
    mind, it might be physically easy to remove and atom but an impossibility
    to add it back especially if the created voids are smeared out.\n
    Removers are called generators but they behave like selectors. Instead
    of applying a certain move on a group of atoms, they normally pick atoms
    from defined atoms list and apply no moves on those. 'move' and
    'transform_coordinates' methods are not implemented in this class of
    generators and a usage error will be raised if called. 'pick_from_list'
    method is used instead and must be overloaded by all RemoveGenerator
    subclasses.

    **N.B. This class can't be instantiated but its sub-classes might be.**

    :Parameters:
        #. group (None, Group): The group instance which is this case must be
           fullrmc EmptyGroup.
        #. maximumCollected (None, Integer): The maximum number allowed of
           atoms to be removed and collected from atomic configuration by the
           stochastic engine. This property is general to the system and
           checks engine's collected atoms not the number of removed atoms
           via this generator. If None is given, the remover will not
           check for the number of already removed atoms before attempting
           a remove.
        #. allowFittingScaleFactor (bool): Constraints and especially
           experimental ones have a scale factor constant that can be fit.
           Fitting a scale factor happens at stochastic engine's runtime
           at a certain fitting frequency. If this flag set to True,
           then fitting the scale factor will be allowed upon removing atoms.
           When set to False, fitting the constraint scale factor will be
           forbidden upon removing atoms. By default, allowFittingScaleFactor
           is set to False because it's more logical to allow removing only
           atoms that enhances the total standard error without rescaling
           the model's data.
        #. atomsList (None,list,set,tuple,np.ndarray): The list of atomss
           index to chose and remove from.
    """
    def __init__(self, group=None, maximumCollected=None, allowFittingScaleFactor=False, atomsList=None):
        if self.__class__.__name__ == "RemoveGenerator":
            raise Exception(LOGGER.error("%s instanciation is not allowed"%(self.__class__.__name__)))
        super(RemoveGenerator, self).__init__(group=group)
        # set collectorState
        self._collectorState = None
        # set maximum collected
        self.set_maximum_collected(maximumCollected)
        # set maximum collected
        self.set_allow_fitting_scale_factor(allowFittingScaleFactor)
        # set maximum collected
        self.set_atoms_list(atomsList)

    @property
    def atomsList(self):
        """Atoms list from which atoms will be picked to attempt removal."""
        return self.__atomsList

    @property
    def allowFittingScaleFactor(self):
        """Whether to allow constraints to fit their scale factor upon
        removing atoms."""
        return self.__allowFittingScaleFactor

    @property
    def maximumCollected(self):
        """Maximum collected atoms allowed."""
        return self.__maximumCollected

    def check_group(self, group):
        """
        Check the generator's group.

        :Parameters:
            #. group (Group): The group instance.
        """
        from fullrmc.Core.Group import EmptyGroup
        if isinstance(group, EmptyGroup):
            return True, ""
        else:
            return False, "Only fullrmc EmptyGroup is allowed for CollectorGenerator"

    def set_maximum_collected(self, maximumCollected):
        """
        Set maximum collected number of atoms allowed.

        :Parameters:
            #. maximumCollected (None, Integer): The maximum number allowed of
               atoms to be removed and collected from atomic configuration by
               the stochastic engine. This property is general to the system and
               checks engine's collected atoms not the number of removed atoms
               via this generator. If None is given, the remover will not
               check for the number of already removed atoms before attempting
               a remove.
        """
        if maximumCollected is not None:
            assert is_integer(maximumCollected), LOGGER.error("maximumCollected must be an integer")
            maximumCollected = INT_TYPE(maximumCollected)
            assert maximumCollected>0, LOGGER.error("maximumCollected must be bigger than 0")
        self.__maximumCollected = maximumCollected

    def set_allow_fitting_scale_factor(self, allowFittingScaleFactor):
        """
        Set allow fitting scale factor flag.

        :Parameters:
            #. allowFittingScaleFactor (bool): Constraints and especially
               experimental ones have a scale factor constant that can be fit.
               Fitting a scale factor happens at stochastic engine's runtime
               at a certain fitting frequency. If this flag set to True,
               then fitting the scale factor will be allowed upon removing
               atoms. When set to False, fitting the constraint scale factor
               will be forbidden upon removing atoms. By default,
               allowFittingScaleFactor is set to False because it's more
               logical to allow removing only atoms that enhances the total
               standard error without rescaling the model's data.
        """
        assert isinstance(allowFittingScaleFactor, bool), LOGGER.error("allowFittingScaleFactor must be boolean")
        self.__allowFittingScaleFactor = allowFittingScaleFactor

    def set_atoms_list(self, atomsList):
        """
        Set atoms index list from which atoms will be picked to attempt removal.
        This method must be overloaded and not be called from this class but
        from its children. Otherwise a usage error will be raised.

        :Parameters:
            #. atomsList (None, list,set,tuple,np.ndarray): The list of atoms
               index to chose and remove from.
        """
        if atomsList is not None:
            C = _Container()
            # add container
            if not C.is_container('removeAtomsList'):
                C.add_container('removeAtomsList')
            # check if atomsList already defined
            loc = C.get_location_by_hint(atomsList)
            if loc is not None:
                atomsList = C.get_value(loc)
            else:
                assert isinstance(atomsList, (list,tuple,np.ndarray)), LOGGER.error("atomsList must be either a list or a numpy.array")
                CL = []
                for idx in atomsList:
                    assert is_integer(idx), LOGGER.error("atomsList items must be integers")
                    assert idx>=0, LOGGER.error("atomsList item must equal or bigger than 0")
                    CL.append(INT_TYPE(idx))
                setCL = set(CL)
                assert len(setCL) == len(CL), LOGGER.error("atomsList redundancy is not allowed")
                AL = np.array(CL, dtype=INT_TYPE)
                # add swapList to container
                C.set_value(container='removeAtomsList', value=AL, hint=atomsList)
                atomsList = AL
        # set atomsList attribute
        self.__atomsList = atomsList
        # reset collector state
        self._collectorState = None

    def move(self, coordinates):
        """
        Moves coordinates.
        This method must NOT be overloaded in MoveGenerator sub-classes.

        :Parameters:
            #. coordinates (np.ndarray): Not used here.
        """
        raise Exception(LOGGER.error("%s '%s' is not allowed in removes generators"%(self.__class__.__name__,inspect.stack()[0][3])))

    def transform_coordinates(self, coordinates, argument):
        """
        This method must NOT be overloaded in MoveGenerator sub-classes.

        :Parameters:
            #. coordinates (np.ndarray): Not used here.
               the translation.
            #. argument (object): Not used here.
        """
        raise Exception(LOGGER.error("%s '%s' is not allowed in removes generators"%(self.__class__.__name__,inspect.stack()[0][3])))

    def pick_from_list(self, engine):
        """
        This method must be overloaded in all RemoveGenerator sub-classes.

        :Parameters:
            #. engine (Engine): stochastic engine calling the method.
        """
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))


class SwapGenerator(MoveGenerator):
    """
    It is a particular move generator that instead of generating a
    move upon a group of atoms, it will exchange the group atom positions
    with other atoms from a defined swapList.
    Because the swapList can be big, swapGenerator can be assigned to
    multiple groups at the same time under the condition of all groups
    having the same length.\n

    During stochastic engine runtime, whenever a swap generator is encountered,
    all sophisticated selection recurrence modes such as (refining, exploring)
    will be reduced to simple recurrence.\n

    This class can't be instantiated but its sub-classes might be.

    :Parameters:
        #. group (None, Group): The group instance.
        #. swapLength (Integer): The swap length that defines the length of
           the group and the length of the every swap sub-list in swapList.
        #. swapList (None, List): List of atoms index.
           If None is given, no swapping or exchanging will be performed.
           If List is given, it must contain lists of atom indexes where every
           sub-list must have the same number of atoms as the group.
    """
    def __init__(self, group=None, swapLength=1, swapList=None):
        super(SwapGenerator, self).__init__(group=group)
        # set swap length
        self.set_swap_length(swapLength)
        # set swap list
        self.set_swap_list(swapList)
        #  initialize swapping variables
        self.__groupAtomsIndexes = None
        self.__swapAtomsIndexes  = None
        # reset collector state
        self._collectorState = None

    @property
    def swapLength(self):
        """ Swap length."""
        return self.__swapLength

    @property
    def swapList(self):
        """ Swap list."""
        return self.__swapList

    @property
    def groupAtomsIndexes (self):
        """ Last selected group atoms index."""
        return self.__groupAtomsIndexes

    @property
    def swapAtomsIndexes(self):
        """ Last swap atoms index."""
        return self.__swapAtomsIndexes

    def set_swap_length(self, swapLength):
        """
        Set swap length. it will empty and reset swaplist automatically.

        :Parameters:
            #. swapLength (Integer): The swap length that defines the length
               of the group and the length of the every swap sub-list in
               swapList.
        """
        assert is_integer(swapLength), LOGGER.error("swapLength must be an integer")
        swapLength = INT_TYPE(swapLength)
        assert swapLength>0, LOGGER.error("swapLength must be bigger than 0")
        self.__swapLength = swapLength
        self.__swapList   = ()
        # set uncollected atoms swapList
        self._remainingAtomsSwapList  = self.__swapList
        # reset collector state
        self._collectorState = None

    def set_group(self, group):
        """
        Set the MoveGenerator group.

        :Parameters:
            #. group (None, Group): group instance.
        """
        MoveGenerator.set_group(self, group)
        if self.group is not None:
            assert len(self.group) == self.__swapLength, LOGGER.error("SwapGenerator groups length must be equal to swapLength.")

    def set_swap_list(self, swapList):
        """
        Set the swap-list to exchange atoms position from.

        :Parameters:
            #. swapList (None, List): The list of atoms.\n
               If None is given, no swapping or exchanging will be performed.\n
               If List is given, it must contain lists of atom indexes where
               every sub-list length must be equal to swapLength.
        """
        C = _Container()
        # add container
        if not C.is_container('swapList'):
            C.add_container('swapList')
        # check if swapList already defined
        loc = C.get_location_by_hint(swapList)
        if loc is not None:
            self.__swapList = C.get_value(loc)
        elif swapList is None:
            self.__swapList = ()
        else:
            SL = []
            assert isinstance(swapList, (list,tuple)), LOGGER.error("swapList must be a list")
            for sl in swapList:
                assert isinstance(sl, (list,tuple)), LOGGER.error("swapList items must be a list")
                subSL = []
                for num in sl:
                    assert is_integer(num), LOGGER.error("swapList sub-list items must be integers")
                    num = INT_TYPE(num)
                    assert num>=0, LOGGER.error("swapList sub-list items must be positive")
                    subSL.append(num)
                assert len(set(subSL))==len(subSL), LOGGER.error("swapList items must not have any redundancy")
                if self.swapLength is not None:
                    assert len(subSL) == self.swapLength, LOGGER.error("swapList item length must be equal to swapLength")
                SL.append(np.array(subSL, dtype=INT_TYPE))
            self.__swapList = tuple(SL)
            # add swapList to container
            C.set_value(container='swapList', value=self.__swapList, hint=swapList)
        # set uncollected atoms swapList
        self._remainingAtomsSwapList  = self.__swapList
        # reset collector state
        self._collectorState = None

    def append_to_swap_list(self, subList):
        """
        Append a sub list to swap list.

        :Parameters:
            #. subList (List): The sub-list of atoms index to append
               to swapList.
        """
        assert isinstance(subList, (list,tuple)), LOGGER.error("subList must be a list")
        subSL = []
        for num in subList:
            assert is_integer(num), LOGGER.error("subList items must be integers")
            num = INT_TYPE(num)
            assert num>=0, LOGGER.error("subList items must be positive")
            subSL.append(num)
        assert len(set(subSL))==len(subSL), LOGGER.error("swapList items must not have any redundancy")
        assert len(subSL) == self.__swapLength, LOGGER.error("swapList item length must be equal to swapLength")
        # append
        self.__swapList = list(self.__swapList)
        subSL = np.array(subSL, dtype=INT_TYPE)
        self.__swapList.append(subSL)
        self.__swapList = tuple(self.__swapList)
        # set uncollected atoms swapList
        self._remainingAtomsSwapList  = self.__swapList
        # reset collector state
        self._collectorState = None

    def _set_remaining_atoms_swap_list(self, engine):
        collectorState = engine._atomsCollector.state
        # check engine's atomsCollector state
        if collectorState == self._collectorState or not len(engine._atomsCollector):
            self._collectorState = collectorState
            return
        C = _Container()
        # add container
        if not C.is_container('swapList'):
            C.add_container('swapList')
        # get swapList location
        loc = C.get_location_by_hint(self.swapList)
        # if location exists
        if loc is not None:
            remainingAtomsSwapList = C.get_value(loc)
            # it must be a dict
            if not isinstance(remainingAtomsSwapList, dict):
                remainingAtomsSwapList = None
            # collector state must be the same as engineCollectorState
            elif remainingAtomsSwapList['collectorState'] != collectorState:
                remainingAtomsSwapList = None
            # if same as engineCollectorState
            else:
                remainingAtomsSwapList = remainingAtomsSwapList['remainingAtomsSwapList']
        # if location doesn't exit
        else:
            remainingAtomsSwapList = None
        # in case swapList needs to be rebuilt
        if remainingAtomsSwapList is None:
            remainingAtomsSwapList = []
            for sl in self.swapList:
                if engine._atomsCollector.any_collected(sl):
                    continue
                remainingAtomsSwapList.append(sl)
            # add to container
            value = {'remainingAtomsSwapList':remainingAtomsSwapList, 'collectorState':collectorState}
            C.set_value(container='swapList', value=value, hint=self.swapList)
        # set remainingAtomsSwapList
        self._remainingAtomsSwapList = remainingAtomsSwapList
        # update collectorState
        self._collectorState = collectorState

    def get_ready_for_move(self, engine, groupAtomsIndexes):
        """
        Set the swap generator ready to perform a move. Unlike a normal
        move generator, swap generators will affect not only the selected
        atoms but other atoms as well. Therefore at stochastic engine runtime,
        selected atoms will be extended to all affected atoms by the swap.\n
        This method is called automatically upon stochastic engine runtime
        to ensure that all affect atoms with the swap are updated.

        :Parameters:
            #. engine (fullrmc.Engine): The stochastic engine calling for
               the move.
            #. groupAtomsIndexes (numpy.ndarray): The atoms index to swap.

        :Returns:
            #. indexes (numpy.ndarray): All the atoms involved in the swap move
               including the given groupAtomsIndexes.
        """
        # update and set _remainingAtomsSwapList and _collectorState
        self._set_remaining_atoms_swap_list(engine=engine)
        # select
        self.__groupAtomsIndexes = groupAtomsIndexes
        # check if existing atoms swap list is not empty. if not swap with itself.
        if len(self._remainingAtomsSwapList):
            self.__swapAtomsIndexes  = self._remainingAtomsSwapList[ randint(0,len(self._remainingAtomsSwapList)-1) ]
        else:
            self.__swapAtomsIndexes = self.__groupAtomsIndexes
        return np.concatenate( (self.__groupAtomsIndexes,self.__swapAtomsIndexes) )


class PathGenerator(MoveGenerator):
    """
    PathGenerator is a MoveGenerator sub-class where moves definitions
    are pre-stored in a path and get pulled out at every move step.\n

    This class can't be instantiated but its sub-classes might be.

    :Parameters:
        #. group (None, Group): The group instance.
        #. path (None, list): The list of moves.
        #. randomize (boolean): Whether to pull moves randomly from path or
           pull moves in order at every step.
    """

    def __init__(self, group=None, path=None, randomize=False):
        super(PathGenerator, self).__init__(group=group)
        # set path
        self.set_path(path)
        # set randomize
        self.set_randomize(randomize)
        # initialize flags
        self.__initialize_path_generator__()

    def __initialize_path_generator__(self):
        self.__step = 0

    @property
    def step(self):
        """ Current step number."""
        return self.__step

    @property
    def path(self):
        """ Path list of moves."""
        return self.__path

    @property
    def randomize(self):
        """ Randomize flag."""
        return self.__randomize

    def check_path(self, path):
        """
        Check the generator's path.\n

        This method must be overloaded in all PathGenerator sub-classes.

        :Parameters:
            #. path (list): The list of moves.
        """
        raise Exception(LOGGER.error("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def normalize_path(self, path):
        """
        Normalizes all path moves. It is called automatically upon
        set_path method is called.\n

        This method can be overloaded in all MoveGenerator sub-classes.

        :Parameters:
            #. path (list): The list of moves.

        :Returns:
            #. path (list): The list of moves.
        """
        return list(path)

    def set_path(self, path):
        """
        Set the moves path.

        :Parameters:
            #. path (list): The list of moves.
        """
        valid, message = self.check_path(path)
        if not valid:
            LOGGER.error(message)
            raise Exception(message)
        # normalize path
        self.__path = self.normalize_path( path )
        # reset generator
        self.__initialize_path_generator__()

    def set_randomize(self, randomize):
        """
        Set whether to randomize moves selection.

        :Parameters:
            #. randomize (boolean): Whether to pull moves randomly from path
               or pull moves in order at every step.
        """
        assert isinstance(randomize, bool), LOGGER.error("randomize must be boolean")
        self.__randomize = randomize

    def move(self, coordinates):
        """
        Move coordinates.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the transformation.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after applying
               the transformation.
        """
        if self.__randomize:
            move = self.__path[ randint(0,len(self.__path)-1) ]
        else:
            move = self.__path[self.__step]
            self.__step = (self.__step+1)%len(self.__path)
        # perform the move
        return self.transform_coordinates(coordinates, argument=move)


class MoveGeneratorCombinator(MoveGenerator):
    """
    MoveGeneratorCombinator combines all moves of a list of MoveGenerators
    and applies it at once.

    :Parameters:
        #. group (None, Group): The constraint stochastic engine.
        #. combination (list): The list of MoveGenerator instances.
        #. shuffle (boolean): Whether to shuffle generator instances at
           every move or to combine moves in the list order.


    .. code-block:: python

        # import fullrmc modules
        from fullrmc.Engine import Engine
        from fullrmc.Core.MoveGenerator import MoveGeneratorCombinator
        from fullrmc.Generators.Translations import TranslationGenerator
        from fullrmc.Generators.Rotations import RotationGenerator

        # create engine
        ENGINE = Engine(path='my_engine.rmc')

        # set pdb file
        ENGINE.set_pdb('system.pdb')

        # Add constraints ...
        # Re-define groups if needed ...

        ##### Define each group move generator as a combination of a translation and a rotation. #####
        # create recursive group selector. Recurrence is set to 20 with explore flag set to True.
        # shuffle is set to True which means that at every selection the order of move generation
        # is random. At one step a translation is performed prior to rotation and in another step
        # the rotation is performed at first.
        # selected from the collector.
        for g in ENGINE.groups:
            # create translation generator
            TMG = TranslationGenerator(amplitude=0.2)
            # create rotation generator only when group length is bigger than 1.
            if len(g)>1:
                RMG = RotationGenerator(amplitude=2)
                MG  = MoveGeneratorCombinator(collection=[TMG,RMG],shuffle=True)
            else:
                MG  = MoveGeneratorCombinator(collection=[TMG],shuffle=True)
            g.set_move_generator( MG )
    """

    def __init__(self, group=None, combination=None, shuffle=False):
        # set combination
        self.__combination = []
        # initialize
        super(MoveGeneratorCombinator, self).__init__(group=group)
        # set path
        self.set_combination(combination=combination)
        # set randomize
        self.set_shuffle(shuffle=shuffle)

    def _codify__(self, name='generator', group=None, addDependencies=True):
        assert isinstance(name, basestring), LOGGER.error("name must be a string")
        assert re.match('[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None, LOGGER.error("given name '%s' can't be used as a variable name"%name)
        dependencies = collections.OrderedDict()
        dependencies['from fullrmc.Core import MoveGenerator'] = True
        code         = []
        combination  = []
        # codify generators
        for idx, gen in enumerate(self.__combination):
            nm      = '%s_%i'%(name,idx)
            dep, cd = gen._codify__(group=None, name=nm, addDependencies=True)
            code.append(cd)
            combination.append(nm)
            for d in dep:
                _ = dependencies.setdefault(d,True)
        # codify combinator
        code.append("{name} = MoveGenerator.MoveGeneratorCombinator\
(group={group}, combination=[{combination}], shuffle={shuffle})"
.format(name=name, group=group, combination=', '.join(combination), shuffle=self.shuffle))
        # set dependencies
        dependencies = list(dependencies)
        # add dependencies
        if addDependencies:
            code = dependencies + [''] + code
        # return
        return dependencies, '\n'.join(code)

    @property
    def shuffle(self):
        """ Shuffle flag."""
        return self.__shuffle

    @property
    def combination(self):
        """ Combination list of MoveGenerator instances."""
        return self.__combination

    def check_group(self, group):
        """
        Checks the generator's group.
        This methods always returns True because normally all combination
        MoveGenerator instances groups are checked.\n

        This method must NOT be overloaded unless needed.

        :Parameters:
            #. group (Group): the Group instance
        """
        return True, ""

    def set_group(self, group):
        """
        Set the MoveGenerator group.

        :Parameters:
            #. group (None, Group): group instance.
        """
        MoveGenerator.set_group(self, group)
        for mg in self.__combination:
            mg.set_group(group)

    def set_combination(self, combination):
        """
        Set the generators combination list.

        :Parameters:
            #. combination (list): The list of MoveGenerator instances.
        """
        assert isinstance(combination, (list,set,tuple)), LOGGER.error("combination must be a list")
        assert len(combination)>1, LOGGER.error("Combination list must contain more than 1 item")
        for c in combination:
            assert isinstance(c, MoveGenerator), LOGGER.error("every item in combination list must be a MoveGenerator instance")
            assert not isinstance(c, SwapGenerator), LOGGER.error("SwapGenerator is not allowed to be combined")
            assert not isinstance(c, RemoveGenerator), LOGGER.error("RemoveGenerator is not allowed to be combined")
            c.set_group(self.group)
        self.__combination = combination

    def set_shuffle(self, shuffle):
        """
        Set whether to shuffle moves generator.

        :Parameters:
            #. shuffle (boolean): Whether to shuffle generator instances at
               every move or to combine moves in the list order.
        """
        assert isinstance(shuffle, bool), LOGGER.error("shuffle must be boolean")
        self.__shuffle = shuffle

    def move(self, coordinates):
        """
        Move coordinates.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the transformation.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after applying
               the transformation.
        """
        indexes = range(len(self.__combination))
        if self.__shuffle:
            shuffle( indexes )
        # create the move combination
        for idx in indexes:
            coordinates = self.__combination[idx].move(coordinates)
        return coordinates


class MoveGeneratorCollector(MoveGenerator):
    """
    MoveGeneratorCollector collects MoveGenerators instances and applies
    the move of one instance at every step.

    :Parameters:
        #. group (None, Group): The constraint stochastic engine.
        #. collection (list): The list of MoveGenerator instances.
        #. randomize (boolean): Whether to pull MoveGenerator instance
           randomly from collection list or in order.
        #. weights (None, list): Generators selections Weights list.
           It must be None for equivalent weighting or list of
           (generatorIndex, weight) tuples.
           If randomize is False, weights list is ignored upon generator
           selection from collection.

    .. code-block:: python

        # import fullrmc modules
        from fullrmc.Engine import Engine
        from fullrmc.Core.MoveGenerator import MoveGeneratorCollector
        from fullrmc.Generators.Translations import TranslationGenerator
        from fullrmc.Generators.Rotations import RotationGenerator

        # create engine
        ENGINE = Engine(path='my_engine.rmc')

        # set pdb file
        ENGINE.set_pdb('system.pdb')

        # Add constraints ...
        # Re-define groups if needed ...

        ##### Define each group move generator as a combination of a translation and a rotation. #####
        # create recursive group selector. Recurrence is set to 20 with explore flag set to True.
        # randomize is set to True which means that at every selection a generator is randomly
        # selected from the collector.
        for g in ENGINE.groups:
            # create translation generator
            TMG = TranslationGenerator(amplitude=0.2)
            # create rotation generator only when group length is bigger than 1.
            if len(g)>1:
                RMG = RotationGenerator(amplitude=2)
                MG  = MoveGeneratorCollector(collection=[TMG,RMG],randomize=True)
            else:
                MG  = MoveGeneratorCollector(collection=[TMG],randomize=True)
            g.set_move_generator( MG )

    """
    def __init__(self, group=None, collection=None, randomize=True, weights=None):
        # set collection
        self.__collection = []
        # initialize
        super(MoveGeneratorCollector, self).__init__(group=group)
        # set path
        self.set_collection(collection)
        # set randomize
        self.set_randomize(randomize)
        # set weights
        self.set_weights(weights)
        # initialize flags
        self.__initialize_generator()

    def _codify__(self, name='generator', group=None, addDependencies=True):
        assert isinstance(name, basestring), LOGGER.error("name must be a string")
        assert re.match('[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None, LOGGER.error("given name '%s' can't be used as a variable name"%name)
        dependencies = collections.OrderedDict()
        dependencies['from fullrmc.Core import MoveGenerator'] = True
        code        = []
        collection  = []
        weights     = [(idx, w) for idx, w in enumerate(self.__generatorsWeight) if w!=1]
        # codify generators
        for idx, gen in enumerate(self.__collection):
            nm      = '%s_%i'%(name,idx)
            dep, cd = gen._codify__(group=None, name=nm, addDependencies=True)
            code.append(cd)
            collection.append(nm)
            for d in dep:
                _ = dependencies.setdefault(d,True)
        # codify combinator
        code.append("{name} = MoveGenerator.MoveGeneratorCollector\
(group={group}, collection=[{collection}], randomize={randomize}, weights={weights})"
.format(name=name, group=group, collection=', '.join(collection),
        weights=weights,randomize=self.randomize))
        # add dependencies
        if addDependencies:
            code = list(dependencies) + [''] + code
        # return
        return list(dependencies), '\n'.join(code)

    def __initialize_generator(self):
        self.__step = 0

    def __check_single_weight(self, w):
        """Check a single group weight tuple format."""
        assert isinstance(w, (list,set,tuple)),LOGGER.error("weights list items must be tuples")
        assert len(w)==2, LOGGER.error("weights list tuples must have exactly 2 items")
        idx  = w[0]
        wgt = w[1]
        assert is_integer(idx), LOGGER.error("weights list tuples first item must be an integer")
        idx = INT_TYPE(idx)
        assert idx>=0, LOGGER.error("weights list tuples first item must be positive")
        assert idx<len(self.__collection), LOGGER.error("weights list tuples first item must be smaller than the number of generators in collection")
        assert is_number(wgt), LOGGER.error("weights list tuples second item must be an integer")
        wgt = FLOAT_TYPE(wgt)
        assert wgt>0, LOGGER.error("weights list tuples first item must be bigger than 0")
        # all True return idx and weight
        return idx, wgt

    @property
    def randomize(self):
        """ Randomize flag."""
        return self.__randomize

    @property
    def collection(self):
        """ List of MoveGenerator instances."""
        return self.__collection

    @property
    def generatorsWeight(self):
        """ Generators selection weights list."""
        return self.__generatorsWeight

    @property
    def selectionScheme(self):
        """ Selection scheme."""
        return self.__selectionScheme

    def set_group(self, group):
        """
        Set the MoveGenerator group.

        :Parameters:
            #. group (None, Group): group instance.
        """
        MoveGenerator.set_group(self, group)
        for mg in self.__collection:
            mg.set_group(group)

    def check_group(self, group):
        """
        Check the generator's group. This methods always returns True
        because normally all collection MoveGenerator instances groups
        are checked.\n

        This method must NOT be overloaded unless needed.

        :Parameters:
            #. group (Group): the Group instance.
        """
        return True, ""

    def set_collection(self, collection):
        """
        Set the generators instances collection list.

        :Parameters:
            #. collection (list): The list of move generator instance.
        """
        assert isinstance(collection, (list,set,tuple)), LOGGER.error("collection must be a list")
        collection = list(collection)
        for c in collection:
            assert isinstance(c, MoveGenerator), LOGGER.error("every item in collection list must be a MoveGenerator instance")
            assert not isinstance(c, SwapGenerator), LOGGER.error("SwapGenerator is not allowed to be collected")
            assert not isinstance(c, SwapGenerator), LOGGER.error("RemoveGenerator is not allowed to be collected")
            c.set_group(self.group)
        self.__collection = collection
        # reset generator
        self.__initialize_generator()

    def set_randomize(self, randomize):
        """
        Set whether to randomize MoveGenerator instance selection
        from collection list.

        :Parameters:
            #. randomize (boolean): Whether to pull MoveGenerator instance
               randomly from collection list or in order.
        """
        assert isinstance(randomize, bool), LOGGER.error("randomize must be boolean")
        self.__randomize = randomize

    def set_weights(self, weights):
        """
        Set groups selection weighting scheme.

        :Parameters:
            #. weights (None, list): Generators selections Weights list.
               It must be None for equivalent weighting or list of
               (generatorIndex, weight) tuples.
               If randomize is False, weights list is ignored upon generator
               selection from collection.
        """
        generatorsWeight = np.ones(len(self.__collection), dtype=FLOAT_TYPE)
        if weights is not None:
            assert isinstance(weights, (list,set,tuple)),LOGGER.error("weights must be a list")
            for w in weights:
                idx, wgt = self.__check_single_weight(w)
                # update groups weight
                generatorsWeight[idx] = wgt
        # set groups weight
        self.__generatorsWeight = generatorsWeight
        # create selection histogram
        self.set_selection_scheme()

    def set_selection_scheme(self):
        """ Set selection scheme. """
        cumsumWeights = np.cumsum(self.__generatorsWeight, dtype=FLOAT_TYPE)
        self.__selectionScheme = cumsumWeights/cumsumWeights[-1]

    def move(self, coordinates):
        """
        Move coordinates.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the transformation.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after applying
               the transformation.
        """
        if self.__randomize:
            index = INT_TYPE( np.searchsorted(self.__selectionScheme, generate_random_float()) )
            moveGenerator = self.__collection[ index ]
        else:
            moveGenerator = self.__collection[self.__step]
            self.__step   = (self.__step+1)%len(self.__collection)
        # perform the move
        return moveGenerator.move(coordinates)

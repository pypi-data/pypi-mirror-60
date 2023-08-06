"""
Swaps contains all swap or atoms position exchange MoveGenerator classes.

.. inheritance-diagram:: fullrmc.Generators.Swaps
    :parts: 1

"""
# standard libraries imports
from __future__ import print_function
import re

# external libraries imports
import numpy as np

# fullrmc imports
from ..Globals import INT_TYPE, FLOAT_TYPE, LOGGER
from ..Globals import str, long, unicode, bytes, basestring, range, xrange, maxint
from ..Core.Collection import is_number, is_integer
from ..Core.MoveGenerator import  MoveGenerator, SwapGenerator
from ..Core.Collection import _Container

class SwapPositionsGenerator(SwapGenerator):
    """
    Generates positional swapping between atoms of the selected group and
    other atoms randomly selected from swapList.

    :Parameters:
        #. group (None, Group): The group instance.
        #. swapLength (Integer): The swap length that defines the length
           of the group and the length of the every swap sub-list in swapList.
        #. swapList (None, List): The list of atoms.\n
           If None is given, no swapping or exchanging will be performed.\n
           If List is given, it must contain lists of atoms where every
           sub-list must have the same number of atoms as the group.

    .. code-block:: python

        # import fullrmc modules
        from fullrmc.Engine import Engine
        from fullrmc.Generators.Swaps import SwapPositionsGenerator

        # create engine
        ENGINE = Engine(path='my_engine.rmc')

        # set pdb file
        ENGINE.set_pdb('system.pdb')

        # Add constraints ...
        # Re-define groups if needed ...
        # Re-define groups selector if needed ...

        ##### set swap moves between Lithium and Manganese atoms in Li2MnO3 system #####
        # reset engine groups to atoms to insure atomic grouping of all the system's atoms
        ENGINE.set_groups_as_atoms()
        # get all elements list
        elements = ENGINE.allElements
        # create list of lithium atoms indexes
        liIndexes = [[idx] for idx in xrange(len(elements)) if elements[idx]=='li']
        # create list of manganese atoms indexes
        mnIndexes = [[idx] for idx in xrange(len(elements)) if elements[idx]=='mn']
        # create swap generator to lithium atoms
        swapWithLi = SwapPositionsGenerator(swapList=liIndexes)
        # create swap generator to manganese atoms
        swapWithMn = SwapPositionsGenerator(swapList=mnIndexes)
        # set swap generator to groups
        for g in ENGINE.groups:
            # get group's atom index
            idx = g.indexes[0]
            # set swap to manganese for lithium atoms
            if elements[idx]=='li':
                g.set_move_generator(swapWithMn)
            # set swap to lithium for manganese atoms
            elif elements[idx]=='mn':
                g.set_move_generator(swapWithLi)
            # the rest are oxygen atoms. Default RandomTranslation generator are kept.

    """
    def _codify__(self, name='generator', group=None, addDependencies=True):
        assert isinstance(name, basestring), LOGGER.error("name must be a string")
        assert re.match('[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None, LOGGER.error("given name '%s' can't be used as a variable name"%name)
        dependencies = 'from fullrmc.Generators import Swaps'
        code         = []
        if addDependencies:
            code.append(dependencies)
        swapList = self.swapList
        if swapList is not None:
            swapList = [list(sl) for sl in swapList]
        code.append("{name} = Swaps.SwapPositionsGenerator\
(group={group}, swapLength={swapLength}, swapList={swapList})"
.format(name=name, group=group, swapLength=self.swapLength, swapList=swapList))
        # return
        return [dependencies], '\n'.join(code)

    def check_group(self, group):
        """
        Check the generator's group.

        :Parameters:
            #. group (Group): The Group instance.
        """
        return True, ""

    def set_swap_length(self, swapLength):
        """
        Set swap length. It will reset swaplist automatically.

        :Parameters:
            #. swapLength (Integer): The swap length that defines the length
               of the group and the length of the every swap sub-list in
               swapList.
        """
        super(SwapPositionsGenerator, self).set_swap_length(swapLength=swapLength)
        self.__swapArray = np.empty( (self.swapLength,3), dtype=FLOAT_TYPE )

    def transform_coordinates(self, coordinates, argument=None):
        """
        Transform coordinates by swapping. This method is called in every move.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the swapping.
            #. argument (object): Any other argument needed to perform
               the move. In General it's not needed.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after applying
               the move.
        """
        # swap coordinates
        self.__swapArray[:,:] = coordinates[:self.swapLength ,:]
        coordinates[:self.swapLength ,:] = coordinates[self.swapLength :,:]
        coordinates[self.swapLength :,:] = self.__swapArray[:,:]
        # return
        return coordinates


class SwapCentersGenerator(SwapGenerator):
    """
    Computes geometric center of the selected group, and swaps its atoms
    by translation to the atoms geometric center of the other atoms which
    are randomly selected from swapList and vice-versa.

    :Parameters:
        #. group (None, Group): The group instance.
        #. swapList (None, List): The list of atoms.\n
           If None is given, no swapping or exchanging will be performed.\n
           If List is given, it must contain lists of atoms index.

    .. code-block:: python

        # import fullrmc modules
        from fullrmc.Engine import Engine
        from fullrmc.Generators.Swaps import SwapCentersGenerator

        # create engine
        ENGINE = Engine(path='my_engine.rmc')

        # set pdb file
        ENGINE.set_pdb('system.pdb')

        # Add constraints ...
        # Re-define groups if needed ...
        # Re-define groups selector if needed ...

        ##### set swap moves between first 10 molecular groups of a system #####
        # reset engine groups to molecules
        ENGINE.set_groups_as_molecules()
        # set swap generator to the first 10 groups
        GROUPS = [ENGINE.groups[idx] for idx in range(10)]
        for gidx, group in enumerate(GROUPS):
            swapList = [g.indexes for idx,g in enumerate(GROUPS) if idx!=gidx]
            swapGen  = SwapCentersGenerator(swapList=swapList)
            group.set_move_generator(swapGen)
    """
    def __init__(self, group=None, swapList=None):
        super(SwapCentersGenerator, self).__init__(group=group, swapLength=None, swapList=swapList )

    def _codify__(self, name='generator', group=None, addDependencies=True):
        assert isinstance(name, basestring), LOGGER.error("name must be a string")
        assert re.match('[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None, LOGGER.error("given name '%s' can't be used as a variable name"%name)
        dependencies = 'from fullrmc.Generators import Swaps'
        code         = []
        if addDependencies:
            code.append(dependencies)
        swapList = self.swapList
        if swapList is not None:
            swapList = [list(sl) for sl in swapList]
        code.append("{name} = Swaps.SwapPositionsGenerator\
(group={group}, swapList={swapList})"
.format(name=name, group=group, swapList=swapList))
        # return
        return [dependencies], '\n'.join(code)

    @property
    def swapLength(self):
        """ Swap length. In this Case it is always None as
        swapLength is not required for this generator."""
        return self.__swapLength

    def set_swap_length(self, swapLength):
        """
        Set swap length. The swap length that defines the length of the
        group and the length of the every swap sub-list in swapList.
        It will automatically be set to None as SwapCentersGenerator
        does not require a fixed length.

        :Parameters:
            #. swapLength (None): The swap length.
        """
        self.__swapLength = None
        self.__swapList   = ()
        # set uncollected atoms swapList
        self._remainingAtomsSwapList = self.__swapList
        # reset collector state
        self._collectorState = None

    def set_group(self, group):
        """
        Set the MoveGenerator group.

        :Parameters:
            #. group (None, Group): group instance.
        """
        MoveGenerator.set_group(self, group)

    def check_group(self, group):
        """
        Check the generator's group.

        :Parameters:
            #. group (Group): the Group instance.
        """
        return True, ""

    def transform_coordinates(self, coordinates, argument=None):
        """
        Transform coordinates by swapping. This method is called in every move.

        :Parameters:
            #. coordinates (np.ndarray): The coordinates on which to apply
               the swapping.
            #. argument (object): Any other argument needed to perform the
               move. In General it's not needed.

        :Returns:
            #. coordinates (np.ndarray): The new coordinates after
               applying the move.
        """
        # get translation vector
        swapLength    = len(self.groupAtomsIndexes)
        swapsOfCenter = np.mean(coordinates[:swapLength,:], axis=0)
        swapsToCenter = np.mean(coordinates[swapLength :,:], axis=0)
        direction     = swapsToCenter-swapsOfCenter
        # swap by translation
        coordinates[: swapLength,:] += direction
        coordinates[swapLength :,:] -= direction
        # return
        return coordinates

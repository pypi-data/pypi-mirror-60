"""
This module provides a Python interface to the NeighborList class
with supplementary functions.
"""

from typing import List, Union
from _icet import NeighborList
from ase import Atoms
from .structure import Structure


def get_neighbor_lists(structure: Union[Atoms, Structure],
                       cutoffs: List[float],
                       position_tolerance: float) -> List[NeighborList]:
    """
    Returns a list of icet neighbor lists given a configuration and cutoffs.

    Parameters
    ----------
    structure
        atomic configuration
    cutoffs
        positive floats indicating the cutoffs for the various clusters
    position_tolerance
        tolerance applied when comparing positions in Cartesian coordinates
    """

    # deal with different types of structure objects
    if isinstance(structure, Atoms):
        structure = Structure.from_atoms(structure)
    elif not isinstance(structure, Structure):
        msg = ['Unknown structure format']
        msg += ['{} (ClusterSpace)'.format(type(structure))]
        raise Exception(' '.join(msg))

    neighbor_lists = []
    for cutoff in cutoffs:
        nl = NeighborList(cutoff)
        neighbor_lists.append(nl)

    # build the neighbor lists
    for nl in neighbor_lists:
        nl.build(structure=structure, position_tolerance=position_tolerance)

    return neighbor_lists

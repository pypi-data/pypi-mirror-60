from typing import Callable, List, Tuple, Dict
import pandas as pd
import numpy as np


def chromosomal_holdout(chromosomes: List[int], parent_chromosomes:List=None, hyper_parameters:Dict=None) -> Tuple[Callable, str, Dict]:
    """Return a function to create an holdout with given chromosomes.
        hyper_parameters:Dict, additional hyper-parameters used to create the holdout.
    """
    formatted_chromosomes = ["chr{c}".format(c=c) for c in chromosomes]
    parent_chromosomes = parent_chromosomes if parent_chromosomes else []
    formatted_parent_chromosomes = ["chr{c}".format(c=c) for c in parent_chromosomes]

    def holdout(dataset: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """
            dataset:List[pd.DataFrame], the dataset to split. The index is expected to be of the format chr19.70741698
        """
        test_mask = np.array(
            [i.split(".")[0] in formatted_chromosomes for i in dataset[0].index])
        train_mask = np.bitwise_not(test_mask)
        return [
            d[mask] for i, d in enumerate(dataset) for mask in [train_mask, test_mask]
        ]

    return holdout, {
        "chromosomes": "-".join(formatted_chromosomes),
        "parent_chromosomes": "-".join(formatted_parent_chromosomes),
        "hyper_parameters": hyper_parameters
    }


def chromosomal_holdouts(chromosomes_lists: List[Tuple[List[int], List[Tuple]]], parent_chromosomes:List=None, hyper_parameters:Dict=None) -> List[Tuple[Callable, str, List]]:
    """Return a Generator of functions to create an holdouts with given chromosomes.
        chromosomes_lists:List[List], list of arbitrary depth of chromosomal holdouts.
        hyper_parameters:Dict, additional hyper-parameters used to create the holdout.
    """
    return [
        (*chromosomal_holdout(chromosomes, parent_chromosomes, hyper_parameters), None) if sub_lists is None
        else (*chromosomal_holdout(chromosomes, parent_chromosomes, hyper_parameters), chromosomal_holdouts(sub_lists, chromosomes, hyper_parameters))
        for chromosomes, sub_lists in chromosomes_lists
    ]

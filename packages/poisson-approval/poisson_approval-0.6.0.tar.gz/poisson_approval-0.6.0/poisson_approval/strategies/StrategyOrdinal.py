from poisson_approval.strategies.StrategyThreshold import StrategyThreshold
from poisson_approval.utils.DictPrintingInOrderIgnoringZeros import DictPrintingInOrderIgnoringZeros


class StrategyOrdinal(StrategyThreshold):
    """A strategy profile for an ordinal preference profile.

    Parameters
    ----------
    d_ranking_ballot : dict
        Keys are rankings and values are ballots, e.g. ``'abc': 'ab'``. A
        ballot can be ``''`` if the behavior of these voters is not specified in the strategy.
    profile : Profile, optional
        The "context" in which the strategy is used.

    Examples
    --------
        >>> strategy = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
        >>> strategy
        StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
        >>> print(strategy)
        <abc: a, bac: ab, cab: c>
        >>> strategy.abc
        'a'
        >>> strategy.a_bc
        'a'
        >>> strategy.ab_c
        'a'
        >>> strategy.d_ranking_threshold['abc']
        1
    """

    def __init__(self, d_ranking_ballot, profile=None):
        """
            >>> strategy = StrategyOrdinal({'abc': 'non_existing_ballot'})
            Traceback (most recent call last):
            ValueError: Unknown strategy: non_existing_ballot
        """
        # Prepare the dictionary of thresholds
        d_ranking_threshold = DictPrintingInOrderIgnoringZeros()
        for ranking, ballot in d_ranking_ballot.items():
            if ballot == '':
                d_ranking_threshold[ranking] = None
            elif ballot == ranking[0]:
                d_ranking_threshold[ranking] = 1
            elif ballot in {ranking[:2], ranking[1::-1]}:
                d_ranking_threshold[ranking] = 0
            else:
                raise ValueError('Unknown strategy: ' + ballot)
        # Call parent class
        super().__init__(d_ranking_threshold=d_ranking_threshold, profile=profile)

    def __eq__(self, other):
        """Equality test.

        Parameters
        ----------
        other : object

        Returns
        -------
        bool
            True if this strategy is equal to `other`.

        Examples
        --------
            >>> strategy = StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
            >>> strategy == StrategyOrdinal({'abc': 'a', 'bac': 'ab', 'cab': 'c'})
            True
        """
        return isinstance(other, StrategyOrdinal) and self.d_ranking_ballot == other.d_ranking_ballot

    def __repr__(self):
        return 'StrategyOrdinal(%r)' % self.d_ranking_ballot

    def _repr_pretty_(self, p, cycle):  # pragma: no cover
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')

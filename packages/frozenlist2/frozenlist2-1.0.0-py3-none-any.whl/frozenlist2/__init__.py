class frozenlist(list):
    """An immutable list.

    The `frozenlist` class has identical behavior to the :class:`list` class,
    with the following exceptions:

    - Any attempt to modify the list will raise :class:`NotImplementedError`.
    - The list is hashable, if and only if all list elements are hashable.

    **Why not tuple?**

    Although the standard :class:`tuple` provides an immutable sequence,
    it has the unfortunate property that a tuple is never equal to a list,
    even when the tuple/list lengths and all elements are equal.

    This has negative implications for the ergonomics of an API designed
    to return immutable data. Developers typically use lists as the default
    choice for an iterable; if an API instead returns a tuple in order to
    expose immutable data, callers must be vigilant to recall that tuples
    rather than lists are in use, and forgetting this can lead to subtle
    bugs.

    `frozenlist` avoids this problem, so that developers can work with
    immutable sequences without having to fight their natural inclination
    to think in terms of lists.
    """

    def __setitem__(self, *_args, **_kwargs):
        self.__attempted_modify()

    def __delitem__(self, *_args, **_kwargs):
        self.__attempted_modify()

    def __iadd__(self, *_args, **_kwargs):
        self.__attempted_modify()

    def insert(self, *_args, **_kwargs):
        self.__attempted_modify()

    def append(self, *_args, **_kwargs):
        self.__attempted_modify()

    def extend(self, *_args, **_kwargs):
        self.__attempted_modify()

    def pop(self, *_args, **_kwargs):
        self.__attempted_modify()

    def remove(self, *_args, **_kwargs):
        self.__attempted_modify()

    def sort(self, *_args, **_kwargs):
        self.__attempted_modify()

    # hashable if and only if everything within it is hashable
    def __hash__(self):
        return hash(tuple(self))

    def __attempted_modify(self):
        raise NotImplementedError("cannot modify immutable list")

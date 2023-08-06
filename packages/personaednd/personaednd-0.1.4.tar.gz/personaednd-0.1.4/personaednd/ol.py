class Ordo:
    def __init__(
        self,
        iterable: (list, set, tuple),
        data_type: (float, int, str, None),
        sort: bool,
        sort_reverse: bool,
        allow_duplicates: bool,
    ) -> None:
        try:
            if not isinstance(iterable, (list, set, tuple)):
                raise TypeError
        except TypeError:
            exit("iterable: must be of type 'list', 'set', or 'tuple'!")
        self.iterable = isinstance(iterable, tuple) and list(iterable) or iterable
        self.data_type = data_type
        self.sort = sort
        self.reversed_sort = sort_reverse
        self.allow_duplicates = allow_duplicates
        if not self.allow_duplicates:
            duplicates = []
            for x in self.iterable:
                if x not in duplicates:
                    occurrences = self.iterable.count(x) - 1
                    for needle in range(occurrences):
                        duplicates.append(x)
            for duplicate in duplicates:
                if duplicate in self.iterable:
                    self.iterable.remove(duplicate)
        self._adicio()
        self._generis()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __repr__(self):
        return "{}".format(self.iterable)

    def __str__(self):
        return "{}".format(self.iterable)

    def _adicio(self) -> list:
        """Latin for: apply"""
        if self.data_type is not None:
            if issubclass(self.data_type, float):
                self.iterable = [float(x) for x in self.iterable]
            elif issubclass(self.data_type, int):
                self.iterable = [int(x) for x in self.iterable]
            elif issubclass(self.data_type, str):
                self.iterable = [str(x) for x in self.iterable]
        return self.iterable

    def _duplication_check(self, x) -> bool:
        if not self.allow_duplicates and x in self.iterable:
            return False
        return True

    def _generis(self) -> list:
        """Latin for: sort"""
        if self.sort is True:
            self.iterable.sort(reverse=self.reversed_sort)
        return self.iterable

    def adde(self, x) -> list:
        """Latin for: add"""
        try:
            if not self._duplication_check(x):
                raise ValueError
            self.iterable.append(x)
            self._adicio()
            self._generis()
        except ValueError:
            pass
        return self.iterable

    def arbitrium(self, remove_on_pick=True) -> (float, int, str):
        """Latin for: choice"""
        from random import choice

        pick = choice(self.iterable)
        if remove_on_pick:
            self.iterable.remove(pick)
        return pick

    def excludere(self, y: (list, set, tuple)) -> list:
        """Latin for: exclude"""
        if isinstance(y, (list, set, tuple)):
            for x in y:
                if x in self.iterable:
                    self.iterable.remove(x)
        return self.iterable

    def get(self) -> list:
        return self.iterable

    def longitudinem(self) -> int:
        """Latin for: length"""
        return len(self.iterable)

    def minuas(self, x) -> list:
        """Latin for: subtract"""
        if x in self.iterable:
            self.iterable.remove(x)
        return self.iterable

    def simul(self, *args) -> list:
        """Latin for: combine"""
        for arg in args:
            if isinstance(arg, (list, set, tuple)):
                for x in arg:
                    if not self._duplication_check(x):
                        continue
                    self.iterable.append(x)
            elif isinstance(arg, dict):
                for x in arg.values():
                    if not self._duplication_check(x):
                        continue
                    self.iterable.append(x)
            else:
                if not self._duplication_check(arg):
                    continue
                self.iterable.append(arg)
        self._adicio()
        self._generis()
        return self.iterable

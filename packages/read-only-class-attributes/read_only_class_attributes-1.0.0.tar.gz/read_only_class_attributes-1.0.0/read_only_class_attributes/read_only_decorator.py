def read_only(*attrs):
    """
    Class decorator to mark selected attributes of a class as read-only. All
    attributes in ``attrs`` cannot be modified. If ``*`` is present in
    ``attrs`` then no attribute can be modified.

    Parameters
    ----------
    attrs : list of str
        Names of the attributes that should be constants. '*' value will
        make all attributes constant
    """
    def _rebuilt_class(cls):
        class ReadOnlyPropertyClass(cls):
            def __setattr__(self, name, value):
                if "*" in attrs:
                    raise AttributeError(
                            "All attributes of this class are read-only")
                if name in attrs:
                    err = "Cannot modify `{}` as it is marked as read-only"
                    err = err.format(name)
                    raise AttributeError(err)
                return super().__setattr__(name, value)
        return ReadOnlyPropertyClass
    return _rebuilt_class

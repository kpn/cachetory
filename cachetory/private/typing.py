class NotSet:
    """
    Internal type of non-set parameter.

    Used to check for unset parameters where `None` is an acceptable value.
    This also allows type-hinting of sentinel parameters.
    """

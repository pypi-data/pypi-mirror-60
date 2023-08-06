NONE_TYPE_ERROR = "'NoneType' value is not allowed"
NOT_STRING_ERROR = "One of the input values is not a string"


def compare_versions(version_a: str, version_b: str) -> int:
    """Check if the version_a is equal to, greater or less than version_b
        :param version_a: The initial version to check
        :param version_b: The second version to check
        :return: Return a int (0) equal, (1) greater than and (-1) less than
    """
    # Fail first if an invalid argument is given
    if version_a is None or version_b is None:
        raise ValueError(NONE_TYPE_ERROR)
    if not isinstance(version_a, str) or not isinstance(version_b, str):
        raise ValueError(NOT_STRING_ERROR)

    # Obtain a tuple of the each version given
    first_tuple = get_version_tuple(version_a)
    second_tuple = get_version_tuple(version_b)
    if first_tuple == second_tuple:
        return 0
    if first_tuple > second_tuple:
        return 1
    if first_tuple < second_tuple:
        return -1


def get_version_tuple(version: str) -> tuple:
    # Remove any space from the string
    version = version.strip()
    # Transform the string value into a tuple of strings
    return tuple(map(str, (version.split("."))))

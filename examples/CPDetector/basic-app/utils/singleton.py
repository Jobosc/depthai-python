def singleton(class_):
    """
    A decorator to implement the singleton pattern for a class.

    Ensures that only one instance of the class is created. If an instance
    already exists, it returns the existing instance.

    Args:
        class_ (type): The class to be decorated as a singleton.

    Returns:
        function: A function that returns the single instance of the class.
    """
    instances = {}

    def getinstance(*args, **kwargs):
        """
        Returns the single instance of the class, creating it if it does not exist.

        Args:
            *args: Variable length argument list for the class constructor.
            **kwargs: Arbitrary keyword arguments for the class constructor.

        Returns:
            object: The single instance of the class.
        """
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance

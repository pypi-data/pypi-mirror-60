class BaseUtilClass:
    def __init__(self, logger=None):
        """
        All function class should mixin or inherit from thisyou
        :param Logger:
        """
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.logger = logger

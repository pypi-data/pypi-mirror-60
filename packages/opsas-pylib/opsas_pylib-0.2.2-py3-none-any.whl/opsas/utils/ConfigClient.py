import os

import yaml
from jinja2 import Template

from .BasicUtilClass import BaseUtilClass


class ConfigClient(BaseUtilClass):
    """ConfigClient

    render a key-value pair from config file. config file was yaml format with jinja2 support.

    Parameters
    ----------
    config_path : str
        Template config file path
    logger : logging.logger, optional
        Python logger object

    Note
    -------
    os environment can be used in yaml via context os_env

    Example
    -------
    >>> import os
    >>> os.environ.setdefault('env','test')
    >>> configClient = ConfigClient("config.yaml")
    ## config.yaml
    env: {{ os_env.get("env") | default("local",True) }}
    >>> configClient.get('env')
    'test'
    """

    def __init__(self, config_path, logger=None):
        super().__init__(logger)
        self.data_map = self.render_yaml_template(config_path)
        self.logger.info(self.data_map)
        """str: Docstring *after* attribute, with type specified."""

    @property
    def items(self):
        return self.data_map.items()

    def render_yaml_template(self, config_path):
        _ = {}
        try:
            fd = open(config_path, 'r')
            data_str = fd.read()
            fd.close()
            yaml_stream = Template(data_str).render(
                os_env=dict(os.environ)
            )
            _ = yaml.safe_load(yaml_stream)
        except (FileNotFoundError, IOError):
            self.logger.error(f"Error open file {config_path}")
        except Exception as error:
            self.logger.error(error)
        return _

    def get(self, k):
        """Get config value via key"""
        return self.data_map.get(k)

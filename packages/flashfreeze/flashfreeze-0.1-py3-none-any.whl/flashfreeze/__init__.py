import os.path
from importlib import import_module
from yaml import load
from flashfreeze.ffdirectory import FFDirectory
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
import logging

class FlashFreeze(object):
  def __init__(self, config_file_location='~/.flashfreeze/config.yaml'):
    self.config_file_location = config_file_location
    self.config = {}
    self.plugins = {}
    self.directories = {}

    if self.config_file_location and os.path.exists(self.config_file_location):
      self.load_config()
    else:
      logging.debug("No config file specified, or it doesn't exist.")

  def load_config(self):
    with open(self.config_file_location) as stream:
      logging.debug("Reading in configuration file")
      self.config = load(stream, Loader)

    if self.config:
      if 'Directories' in self.config and self.config['Directories']:
        self.directories = {}
        for dir_name in self.config['Directories'].keys():
          d_config = self.config['Directories'][dir_name]
          if 'plugins' in d_config and d_config['plugins']:
            d_config['plugins'] = self.process_plugins(d_config['plugins'])
          self.directories[dir_name] = FFDirectory(d_config)

  def process_plugins(self, plugin_configs):
    plugins = []
    for plugin_name in plugin_configs:
      klass = self.get_plugin(plugin_name)
      plugins.append(klass(plugin_configs[plugin_name]))

    return plugins

  def get_plugin(self, plugin_name):
    if plugin_name not in self.plugins:
      # try to import it
      package = import_module(".%s" % plugin_name.lower(), package="flashfreeze.plugins")

      # get the class and add to our cache
      self.plugins[plugin_name] = getattr(package, plugin_name)

      # if we found it, cool
      if plugin_name in self.plugins:
        return self.plugins[plugin_name]
      else: # oopsy
        pass

  def run(self, directory_name=None):
    if directory_name:
      self.run_directory(directory_name)
    else:
      logging.info("Running all directories")
      for dir_name in self.directories:
        self.run_directory(dir_name)

  def run_directory(self, directory_name):
    logging.info("RUnning directory %s" % directory_name)
    self.directories[directory_name].process()

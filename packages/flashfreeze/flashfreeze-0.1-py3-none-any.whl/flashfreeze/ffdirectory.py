from tempfile import NamedTemporaryFile
import time
import os

from flashfreeze.gitclient import GitClient

class FFDirectory(object):
  def __init__(self, config):
    self.config = config
    self.git = GitClient(config['directory'])

  @property
  def changed_files(self):
    # Add untracked files
    self.git.add_untracked_files()

    # go through and find ones that have been quiet long enough
    modified_files = []

    quiet_time = time.time() - (self.config['quiet_time'] * 60)

    for file in self.git.changed_files:
      path = os.path.join(self.git.working_dir, file)
      if os.path.getmtime(path) <= quiet_time:
        modified_files.append(file)

    return modified_files

  def process(self):
    changes = self.changed_files
    if (changes):
      # use temp file for commit message
      tempfile = NamedTemporaryFile(delete=False)

      # write the commit message
      for plugin in self.config['plugins']:
        plugin.add_context(tempfile)
      tempfile.close()

      # actually commit it all
      self.git.commit(tempfile.name, changes)
      self.git.push()

      # clean up temp file
      os.remove(tempfile.name)

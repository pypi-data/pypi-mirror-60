from git import Repo

class GitClient(object):
  def __init__(self, path, quiet_period=15):
    self.path = path
    self._git = Repo(path)

  @property
  def changed_files(self):
    """Returns list of all files that have changed. This includes both modified files,
    and untracked ones."""
    files = []

    # get list of changed files
    for modified in self._git.index.diff(None):
      files.append(modified.a_path)

    return files + self.untracked_files

  @property
  def untracked_files(self):
    return self._git.untracked_files

  @property
  def working_dir(self):
    return self._git.working_dir

  def add_untracked_files(self, files=None):
    if files == None:
      files = self.untracked_files
    self._git.index.add(files)

  def commit(self, message, files=None):
    if files == None:
      self._git.index.commit(message)
    else:
      self._git.git.commit('-F', message, *files)

  def head_commit(self):
    return self._git.head.commit

  def push(self):
    return self._git.remotes.origin.push()

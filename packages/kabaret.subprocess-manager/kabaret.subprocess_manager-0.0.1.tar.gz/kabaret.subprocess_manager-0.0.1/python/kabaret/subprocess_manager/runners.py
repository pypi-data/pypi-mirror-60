
import sys

from .manager import SubprocessRunner

class PythonREPL(SubprocessRunner):

    @classmethod
    def runner_name(cls):
        return 'Python'

    def keep_terminal(self, version):
        return False

    def executable(self, version):
        return sys.executable
    
    def argv(self, version):
        return []

class Explorer(SubprocessRunner):

    @classmethod
    def runner_name(cls):
        return 'Explorer'

    def show_terminal(self, version):
        return False

    def executable(self, version):
        return 'explorer.exe'
    
    def argv(self, version):
        return []

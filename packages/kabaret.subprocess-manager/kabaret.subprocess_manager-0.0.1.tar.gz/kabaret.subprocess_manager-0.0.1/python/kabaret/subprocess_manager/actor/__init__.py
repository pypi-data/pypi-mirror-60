
import os

from kabaret.app._actor import Actor, Cmd, Cmds

from .. import manager
from .. import runners

class SubprocessManagerCmds(Cmds):
    pass

@SubprocessManagerCmds.cmd
class Get_Group_Names(Cmd):

    def _decode(self, reverse=False):
        self.reverse = reverse
    
    def _execute(self):
        actor = self.actor()
        names = actor.get_group_names()
        if not reversed:
            return names
        return [ n for n in reversed(names) ]

@SubprocessManagerCmds.cmd
class Get_Group_Info(Cmd):

    def _decode(self, group_name):
        self.group_name = group_name
    
    def get_runner_info(self, name, RunnerType):
        return dict(
            name=name,
            versions=RunnerType.supported_versions(),
            config=RunnerType.config(),
        )

    def _execute(self):
        actor = self.actor()
        group = actor.get_group(self.group_name)
        info = {}
        info['config'] = group.config()
        runners = []
        info['runners'] = runners
        for name, runner in group.get_runners():
            runners.append(
                self.get_runner_info(name, runner)
            )
        return info

@SubprocessManagerCmds.cmd
class Get_Runner_Versions(Cmd):

    def _decode(self, runner_name, group_name=None):
        self.runner_name = runner_name
        self.group_name = group_name
    
    def _execute(self):
        runner = self.actor().get_runner(
            self.runner_name, self.group_name
        )
        return runner.supported_versions()

@SubprocessManagerCmds.cmd
class Run(Cmd):

    def _decode(
            self, 
            runner_name, version=None, group_name=None,
            extra_argv=[], extra_env={},
    ):
        self.runner_name = runner_name
        self.version = version
        self.group_name = group_name
        self.extra_argv = extra_argv
        self.extra_env = extra_env

    def _execute(self):
        self.actor().run(
            self.runner_name, 
            self.version,
            self.group_name,
            self.extra_argv,
            self.extra_env,
        )

class PythonREPL(runners.PythonREPL):
    
    CONFIG = {
        'icon':('icons.flow', 'python'),
    }

class Explorer(runners.Explorer):
    
    CONFIG = {
        'icon':('icons.flow', 'explorer'),
    }

class SubprocessManager(Actor):
    
    def __init__(self, session):
        super(SubprocessManager, self).__init__(session)
        self._manager = manager.SubprocessManager()

        # Default Groups and Runners config:
        system_group = self._manager.get_runner_group('System')
        system_group.set_config(
            'icon', ('icons.flow', 'task')
        )
        if os.name == 'nt':
            self._manager.ensure_runner(
                Explorer, group_name=system_group.name
            )
        self._manager.ensure_runner(
            PythonREPL, group_name=system_group.name
        )

    def _create_cmds(self):
        return SubprocessManagerCmds(self)

    def add_runner(self, RunnerType, runner_name=None, group_name=None):
        self._manager.add_runned(RunnerType, runner_name, group_name)
        self.session().dispatch_event(
            'subprocess_manager.runner_added', 
            runner_name=runner_name,
            group_name=group_name,
        )

    def ensure_runner(self, RunnerType, runner_name=None, group_name=None):
        added = self._manager.ensure_runner(RunnerType, runner_name, group_name)
        if added:
            self.session().dispatch_event(
                'subprocess_manager.runner_added', 
                runner_name=runner_name,
                group_name=group_name,
            )

    def get_group_names(self):
        return self._manager.get_runner_group_names()

    def get_group(self, group_name):
        names = self.get_group_names()
        group = self._manager.get_runner_group(group_name)
        if names != self.get_group_names():
            self.session().dispatch_event(
                'subprocess_manager.group_added', 
                group_name=group_name,
            )
        return group

    def get_runner(self, runner_name, group_name):
        return self._manager.get_runner(
            runner_name, group_name
        )

    def run(
        self, 
        runner_name, version=None, group_name=None,
        extra_argv=[], extra_env={}
    ):
        self._manager.run(
            runner_name, version, group_name,
            extra_argv, extra_env
        )
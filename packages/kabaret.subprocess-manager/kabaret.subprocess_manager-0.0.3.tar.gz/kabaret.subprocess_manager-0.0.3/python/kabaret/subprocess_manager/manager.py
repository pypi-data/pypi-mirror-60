
import os
import subprocess

import logging
logger = logging.getLogger(__name__)

class SubprocessRunner(object):

    CONFIG = {}

    @classmethod
    def runner_name(cls):
        return cls.__name__

    @classmethod
    def supported_versions(cls):
        '''
        Returns a list of supported version names.
        Default is to return [None] which means only
        a default unspecified version is supported.
        '''
        return [None]

    @classmethod
    def config(cls):
        '''
        Returns the config dict (default to return cls.CONFIG).
        Subclass can implement this to return a dict
        with whatever your framework needs.
        '''
        return cls.CONFIG

    def __init__(self, manager, extra_argv, extra_env):
        super(SubprocessRunner, self).__init__()
        self._manager = manager
        self._extra_argv = extra_argv
        self._extra_env = extra_env

    def show_terminal(self, version):
        return True

    def keep_terminal(self, version):
        return True

    def executable(self, version):
        '''
        Returns the path of the executable to run.
        '''
        raise NotImplementedError()

    def argv(self, version):
        '''
        Returns the list of arg values for the command to run.
        '''
        raise NotImplementedError()

    def env(self, version):
        '''
        Returns the env to use for the command to run.
        Default is a copy of os.environ
        '''
        return os.environ.copy()
    
    def run(self, version=None):
        cmd = [self.executable(version)]
        cmd.extend(self.argv(version))
        cmd.extend(self._extra_argv)

        env = self.env(version)
        env.update(self._extra_env)
        
        os_flags = {}

        # Disowning processes in linux/mac
        if hasattr(os, 'setsid'):
            os_flags['preexec_fn'] = os.setsid

        # Disowning processes in windows
        if hasattr(subprocess, 'STARTUPINFO'):
            # Detach the process
            os_flags['creationflags'] = subprocess.CREATE_NEW_CONSOLE

            # Hide the process console
            startupinfo = subprocess.STARTUPINFO()
            if self.show_terminal(version):
                flag = '/C'
                if self.keep_terminal(version):
                    flag = '/K'
                cmd = ['cmd', flag] + cmd
            else:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            os_flags['startupinfo'] = startupinfo

        logger.info('Running Subprocess: %r', cmd)
        popen = subprocess.Popen(
            cmd, env=env, **os_flags
        )
        return popen

class RunnersGroup(object):

    def __init__(self, name):
        super(RunnersGroup, self).__init__()
        self.name = name
        self._runners = {}
        self._config = {}
    
    def set_config(self, name, value):
        self._config[name] = value
    
    def get_config(self, name, default):
        return self._config.get(name, default)

    def config(self):
        return self._config.copy()

    def add_runner(self, RunnerType, runner_name=None):
        runner_name = runner_name or RunnerType.runner_name()
        self._runners[runner_name] = RunnerType

    def get_runners(self):
        return sorted(
            self._runners.items()
        )

    def get_runner(self, runner_name):
        return self._runners.get(runner_name, None)

class SubprocessManager(object):

    DEFAULT_GROUP_NAME = 'Other'

    def __init__(self):
        super(SubprocessManager, self).__init__()
        self._runner_groups = []
    
    def get_runner_group_names(self):
        return [g.name for g in self._runner_groups]

    def get_runner_group(self, group_name=None):
        '''
        Returns the runner group, creating it if needed.
        '''
        group_name = group_name or self.DEFAULT_GROUP_NAME
        for group in self._runner_groups:
            if group.name == group_name:
                return group
        
        group = RunnersGroup(group_name)
        self._runner_groups.append(group)
        return group

    def add_runner(self, RunnerType, runner_name=None, group_name=None):
        group = self.get_runner_group(group_name)
        group.add_runner(RunnerType, runner_name)

    def ensure_runner(self, RunnerType, runner_name=None, group_name=None):
        '''
        Returns True if the runner type was added.
        '''
        group = self.get_runner_group(group_name)
        runner_name = runner_name or RunnerType.runner_name()
        runner = group.get_runner(runner_name)
        if runner is None:
            self.add_runner(RunnerType, runner_name, group_name)
            return True # Runner added
        elif runner is not RunnerType:
            raise ValueError(
                'Ensuring Runner {} (name:{}, group:{}):\n'
                'The installed runner is a {} and not a {}'.format(
                    RunnerType.__name__, runner_name, group_name,
                    runner, RunnerType
                )
            )
        else:
            return False # Runner not added, already existed.

    def get_runner(self, runner_name, group_name=None):
        if group_name is not None:
            group = self.get_runner_group(group_name)
            return group.get_runner(runner_name)

        for group in self._runner_groups:
            runner = group.get_runner(runner_name)
            if runner:
                return runner
        
    def run(
        self, 
        runner_name, version=None, group_name=None,
        extra_argv=[], extra_env={},
    ):
        RunnerType = self.get_runner(runner_name, group_name)
        if RunnerType is None:
            raise ValueError(
                'Could not find runner {} in group {}'.format(
                    runner_name, group_name or '<Unspecified>'
                )
            )
        runner = RunnerType(self, extra_argv, extra_env)
        runner.run(version)

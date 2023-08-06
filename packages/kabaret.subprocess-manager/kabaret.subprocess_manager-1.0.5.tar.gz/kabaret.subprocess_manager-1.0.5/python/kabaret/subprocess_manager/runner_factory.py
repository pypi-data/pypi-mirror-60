import os
import subprocess

import logging

logger = logging.getLogger(__name__)


class Runner(object):
    """
    The Runner is able to spawn a subprocess with controled
    command line and environment (among others things).

    """

    TAGS = []
    ICON = None

    @classmethod
    def runner_name(cls):
        """
        Returns the name of the Runner.
        This value does not need to be unic among your runners:
        tags are also used to differenciate them. (but you'll
        probably need to ensure (name,tags) are unique.)
        """

        return cls.__name__

    @classmethod
    def runner_tags(cls):
        """
        Returns a list of tags for this runner.
        Tags are used to group and sort runner in GUIs, and
        to uniquify runners.

        Only the first tag is used to group runners in UIs.

        Default is to return the `TAGS` class attribute.
        """
        return cls.TAGS

    @classmethod
    def has_tags(cls, tags):
        """
        Returns True if all given tags are in `runner_tags()`
        """
        return set(tags).issubset(set(cls.runner_tags()))

    @classmethod
    def runner_icon(cls):
        """
        This value depends on how you entend to use it...
        Default is to return the `ICON` class attribute.
        """
        return cls.ICON

    @classmethod
    def can_edit(cls, filename):
        """
        Must be implemented to return True if the filename
        looks like something supported by this process.

        Default is to return False
        """
        return False

    @classmethod
    def supported_versions(cls):
        """
        Return a list of supported version names.
        A version name of `None` represents the default version.

        Default is to return [None]
        """
        return [None]

    def __init__(self, version=None, label=None, extra_argv=[], extra_env={}):
        super(Runner, self).__init__()
        self.version = version
        self.label = label or self.runner_name()
        self.extra_argv = extra_argv
        self.extra_env = extra_env

        self._popen = None

    def show_terminal(self):
        return True

    def keep_terminal(self):
        return True

    def executable(self):
        """
        Must return the path of the executable to run
        depending on self.version
        """
        raise NotImplementedError()

    def argv(self):
        """
        Must return the list of arg values for the command to run
        including self.extra_argv.
        Default is to return extra_argv
        """
        return self.extra_argv

    def env(self):
        """
        Returns the env to use for the command to run.
        Default is a copy of os.environ and update with
        self.extra_env
        """
        env = os.environ.copy()
        env.update(self.extra_env)
        return env

    def run(self):
        cmd = [self.executable()]
        cmd.extend(self.argv())

        env = self.env()

        os_flags = {}

        # Disowning processes in linux/mac
        if hasattr(os, "setsid"):
            os_flags["preexec_fn"] = os.setsid

        # Disowning processes in windows
        if hasattr(subprocess, "STARTUPINFO"):
            # Detach the process
            os_flags["creationflags"] = subprocess.CREATE_NEW_CONSOLE

            # Hide the process console
            startupinfo = subprocess.STARTUPINFO()
            if self.show_terminal():
                flag = "/C"
                if self.keep_terminal():
                    flag = "/K"
                cmd = ["cmd", flag] + cmd
            else:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            os_flags["startupinfo"] = startupinfo

        logger.info("Running Subprocess: %r", cmd)
        popen = subprocess.Popen(cmd, env=env, **os_flags)
        self.popen = popen

    def is_running(self):
        return self.popen is not None

    def get_log_path(self):
        return None  # not yet functionnal


class Factory(object):
    """
    A Factory is able to find and instanciate registered Runners.
    You manage a collection of Factory with the Factories class.
    """

    def __init__(self, name):
        super(Factory, self).__init__()
        """
        The `name` only purpose is logging info.
        """
        self.name = name
        self._runner_types = []

    def ensure_runner_type(self, RunnerType):
        if RunnerType in self._runner_types:
            return
        self._runner_types.append(RunnerType)

    def list_runner_types(self):
        return list(self._runner_types)

    def runner_tags(self):
        """
        Returns an ordered list of know tags.
        """
        tags = []  # dont use set to keep order
        for RunnerType in self._runner_types:
            for t in RunnerType.runner_tags():
                if t not in tags:
                    tags.append(t)
        return tags

    def find_runners(self, edited_filename=None, tags=[]):
        """
        Returns a list of (runner names, tags) supporting the given
        filename and having given tags.

        An `edited_filename` of `None` will match any RunnerType
        """
        names_and_tags = []
        for RunnerType in self._runner_types:
            if not RunnerType.has_tags(tags):
                continue
            if edited_filename is None or RunnerType.can_edit(edited_filename):
                names_and_tags.append(
                    (RunnerType.runner_name(), RunnerType.runner_tags(),)
                )
        return names_and_tags

    def get_runner_versions(self, runner_name, tags=[]):
        """
        Only the first matching runner is processed.
        If the runner is not found, None is returned.

        Using None as `tags` will match any RunnerType
        with `runner_name`
        """
        for RunnerType in self._runner_types:
            if tags is not None and not RunnerType.has_tags(tags):
                continue
            if RunnerType.runner_name() == runner_name:
                return RunnerType.supported_versions()
        return None

    def get_runner(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
    ):
        """
        Returns the first runner with the given runner_name and tags,
        configured with version, label, extra_arv and extra_env.
        """
        for RunnerType in self._runner_types:
            if RunnerType.runner_name() != runner_name:
                continue
            if not RunnerType.has_tags(tags):
                continue
            return RunnerType(
                version=version,
                label=label,
                extra_argv=extra_argv,
                extra_env=extra_env,
            )
        return None


class Factories(object):

    # NB: I don't use the composition pattern here
    # because I don't want to support a tree of
    # factories.

    def __init__(self):
        super(Factories, self).__init__()
        self._factories = []

    def create_new_factory(self, factory_name):
        """
        Will return a new factory, but WILL NOT REGISTER it.
        """
        return Factory(factory_name)

    def ensure_factory(self, factory):
        if factory in self._factories:
            return
        self._factories.append(factory)

    def list_runner_types(self):
        """
        Returns an ordered list of:
            (factory, RunnerType)
        """
        RunnerTypes = []
        for factory in self._factories:
            for RunnerType in factory.list_runner_types():
                RunnerTypes.append((factory, RunnerType))
        return RunnerTypes

    def runner_tags(self):
        tags = []  # dont use set to keep order
        for factory in self._factories:
            for tag in factory.runner_tags():
                if tag not in tags:
                    tags.append(tag)
        return tags

    def find_runners(self, edited_filename, tags=[]):
        names_and_tags = []  # dont use set to keep order
        for factory in self._factories:
            for nat in factory.find_runners(edited_filename, tags):
                names_and_tags.append(nat)
        return names_and_tags

    def get_runner_versions(self, runner_name, tags=[]):
        """
        Only the first matching runner is processed.
        If the runner is not found, None is returned.
        """
        for factory in self._factories:
            versions = factory.get_runner_versions(runner_name, tags,)
            if versions is not None:
                return versions
        return None

    def get_runner(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
    ):
        """
        Only the first matching runner is processed.
        """
        for factory in self._factories:
            runner = factory.get_runner(
                runner_name, tags, version, label, extra_argv, extra_env,
            )
            if runner is not None:
                return runner
        return None


class SubprocessManager(object):
    """
    The SubprocessManager manages a list of Runner instances.
    """

    def __init__(self):
        super(SubprocessManager, self).__init__()
        self._runners = []

    def get_runner_infos(self):
        """
        Return a list of dict with keys:
            label, name, icon, version, is_running, log_path
        """
        infos = []
        for runner in self._runners:
            infos.append(
                dict(
                    label=runner.label,
                    name=runner.runner_name(),
                    icon=runner.runner_icon(),
                    version=runner.version,
                    is_running=runner.is_running(),
                    log_path=runner.get_log_path(),
                )
            )

    def run(self, runner):
        self._runners.append(runner)
        runner.run()


def test():
    class MyRunner1(Runner):
        TAGS = ["A", "B", "C", "D"]

    class MyRunner2(Runner):
        TAGS = ["C", "D", "E", "F"]

    factory_1 = Factory("F1")
    factory_1.ensure_runner_type(MyRunner1)

    factory_2 = Factory("F2")
    factory_2.ensure_runner_type(MyRunner2)

    factories = Factories()
    factories.ensure_factory(factory_1)
    factories.ensure_factory(factory_2)

    tags = factories.runner_tags()
    print("TAGS:", tags)
    assert tags == ["A", "B", "C", "D", "E", "F"]

    runners = factories.find_runners(None, ["D", "C"])
    print("Runners:", runners)
    assert runners == [
        ("MyRunner1", ["A", "B", "C", "D"]),
        ("MyRunner2", ["C", "D", "E", "F"]),
    ]


if __name__ == "__main__":
    test()

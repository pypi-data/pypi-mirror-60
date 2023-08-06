import os

from kabaret.app._actor import Actor, Cmd, Cmds

from .. import runner_factory
from ..runners import get_system_factory


class SubprocessManagerCmds(Cmds):
    pass


@SubprocessManagerCmds.cmd
class List_Runners(Cmd):
    """
    Returns an ordered list of dicts with keys:
        (
            factory_name,
            group_name,
            group_icon,
            runner_name,
            runner_icon,
            runner_tags,
            version
        )
        NB: one entry per supported version !
    """

    def _decode(self, reverse=False):
        self.reverse = reverse

    def _execute(self):
        collected = []
        factories = self.actor().get_factories()
        last_group_name = None
        for factory, RunnerType in factories.list_runner_types():
            factory_name = factory.name

            runner_name = RunnerType.runner_name()
            runner_icon = RunnerType.runner_icon()
            supported_versions = RunnerType.supported_versions()

            group_name = None
            tags = RunnerType.runner_tags()
            if tags:
                group_name = tags[0]

            if last_group_name is None or group_name != last_group_name:
                last_group_name = group_name
                group_icon = runner_icon

            for version in supported_versions:
                sortable = [
                    factory_name,
                    group_name,
                    group_icon,
                    runner_name,
                    runner_icon,
                ]
                if version is not None:
                    sortable.append(version)
                collected.append(
                    (
                        tuple(sortable),
                        dict(
                            factory_name=factory.name,
                            group_name=group_name,
                            group_icon=group_icon,
                            runner_name=runner_name,
                            runner_icon=runner_icon,
                            runner_tags=tags,
                            version=version,
                        ),
                    )
                )
        collected.sort(reverse=self.reverse)
        return [i[1] for i in collected]


@SubprocessManagerCmds.cmd
class Get_Runner_Versions(Cmd):
    def _decode(self, runner_name, tags=[]):
        self.runner_name = runner_name
        self.tags = tags

    def _execute(self):
        return (
            self.actor()
            .get_factories()
            .get_runner_versions(self.runner_name, self.tags)
        )


@SubprocessManagerCmds.cmd
class Run(Cmd):
    def _decode(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
    ):
        self.runner_name = runner_name
        self.tags = tags
        self.version = version
        self.label = label
        self.extra_argv = extra_argv
        self.extra_env = extra_env

    def _execute(self):
        self.actor().run(
            self.runner_name,
            self.tags,
            self.version,
            self.label,
            self.extra_argv,
            self.extra_env,
        )


class SubprocessManager(Actor):
    def __init__(self, session):
        super(SubprocessManager, self).__init__(session)
        # self._manager = manager.SubprocessManager()
        self._factories = runner_factory.Factories()
        self._subprocess_manager = runner_factory.SubprocessManager()

        # Add default factories:
        self._factories.ensure_factory(get_system_factory())

    def _create_cmds(self):
        return SubprocessManagerCmds(self)

    def get_factories(self):
        return self._factories

    def create_new_factory(self, name):
        return self._factories.create_new_factory(name)

    def ensure_factory(self, runner_factory):
        self._factories.ensure_factory(runner_factory)
        self.session().dispatch_event(
            "subprocess_manager.factory_added", factory_name=runner_factory.name
        )

    def run(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
    ):
        runner = self._factories.get_runner(
            runner_name, tags, version, label, extra_argv, extra_env,
        )
        self._subprocess_manager.run(runner)

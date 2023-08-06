from kabaret import flow


class RunAction(flow.Action):
    def runner_name_and_tags(self):
        """
        Must be implemented to return the name and the tags identifying the
        runner to launch with this action:
            'Blender', ['Previz']

        Using None for tags will skip tag filtering and match
        the first runner with the name.
        """
        raise NotImplementedError()

    def extra_argv(self):
        """
        Returns the extra command line arguments to
        pass to the subprocess.

        Default is to return []
        """
        return []

    def extra_env(self):
        """
        Returns the extra env vars to
        pass to the subprocess.

        Default is to return {}
        """
        return {}

    def get_run_label(self):
        """
        Must return the label of the subprocess
        is the SubprocessManager UIs.

        Default is to return None so that the
        Runner name is used as label.
        """
        return None

    def get_versions(self):
        name, tags = self.runner_name_and_tags()
        return (
            self.root().session().cmds.SubprocessManager.get_runner_versions(name, tags)
        )

    def get_version(self, button):
        """
        If the launched version depends on the clicked button,
        here is the chance to choose it.
        Default is to return None wich always points to the
        defalut version.
        """
        return None

    def run(self, button):
        name, tags = self.runner_name_and_tags()
        self.root().session().cmds.SubprocessManager.run(
            runner_name=name,
            tags=tags,
            version=self.get_version(button),
            label=self.get_run_label(),
            extra_argv=self.extra_argv(),
            extra_env=self.extra_env(),
        )

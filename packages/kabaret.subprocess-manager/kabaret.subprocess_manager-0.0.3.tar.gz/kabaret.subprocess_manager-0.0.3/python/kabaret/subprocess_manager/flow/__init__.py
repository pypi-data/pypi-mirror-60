
from kabaret import flow


class RunAction(flow.Action):

    def runner_name_and_group(self):
        '''
        Must be implemented to return the name and the group of the runner
        to launche with this action.
        The group can be None to use the first runner with the 
        given name.
        '''
        raise NotImplementedError()

    def extra_argv(self):
        return []
    
    def extra_env(self):
        return {}

    def get_versions(self):
        name, group = self.runner_name_and_group()
        return self.root().session().cmds.SubprocessManager.get_runner_versions(
            name, group
        )
    def get_version(self, button):
        '''
        If the launched version depends on the clicked button,
        here is the chance to choose it.
        Default is to return None
        '''
        return None
        
    def run(self, button):
        name, group = self.runner_name_and_group()
        self.root().session().cmds.SubprocessManager.run(
            runner_name=name,
            version=self.get_version(button),
            group_name=group,
            extra_argv=self.extra_argv(),
            extra_env=self.extra_env(),
        )
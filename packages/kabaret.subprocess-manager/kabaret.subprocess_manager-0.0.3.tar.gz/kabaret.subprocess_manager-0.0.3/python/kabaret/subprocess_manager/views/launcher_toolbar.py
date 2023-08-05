from kabaret.app import resources

import kabaret.app.ui.gui.widgets.widget_view
from kabaret.app.ui.gui.widgets.widget_view import (
    ToolBarView,
    QtWidgets, QtGui, QtCore
)


class LauncherToolBar(ToolBarView):

    def __init__(self, *args, **kwargs):
        kwargs['area'] = QtCore.Qt.LeftToolBarArea
        super(LauncherToolBar, self).__init__(*args, **kwargs)

        self._group_tbs = {}
        self.refresh()

    def refresh(self):
        self.clear()
        self.load()

    def clear(self):
        for tb in self._group_tbs.values():
            tb.deleteLater()
        self._group_tbs.clear()

    def load(self):
        for group_name in self.session.cmds.SubprocessManager.get_group_names(
            reverse=True
        ):
            self.ensure_group(group_name)

    def ensure_group(self, group_name):
            info = self.session.cmds.SubprocessManager.get_group_info(
                group_name
            )
            config = info['config']
            icon_ref = config.get(
                'icon', 
                ('icons.gui','cog-wheel-silhouette')
            )

            if group_name not in self._group_tbs:
                tb = QtWidgets.QToolButton(self)
                self.addWidget(tb)
                self._group_tbs[group_name] = tb
            else:
                tb = self._group_tbs[group_name]
            tb.setProperty('hide_arrow', True)
            tb.setText(group_name)
            tb.setToolTip(group_name)
            tb.setPopupMode(tb.InstantPopup)
            tb.setIcon(resources.get_icon(icon_ref))
            tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

            runners = info['runners']
            self.sync_group(group_name, runners)
    
    def sync_group(self, group_name, runners=None):
        # Fetch runners if not provided:
        if runners is None:
            info = self.session.cmds.SubprocessManager.get_group_info(
                group_name
            )
            runners = info['runners']

        # clear all toolbutton actions
        tb = self._group_tbs[group_name]
        actions = tb.actions()
        for action in actions:
            tb.removeAction(action)
            action.deleteLater()

        # create all toolbutton actions
        for runner in runners:
            name = runner['name']
            versions = runner['versions']
            config = runner['config']
            runner_icon = config.get('icon')
            label = name
            for version in versions:
                if version is None:
                    if len(versions) > 1:
                        label = name + ' (Default)'
                else:
                    label = name + ' (%s)'%(version,)
                action = QtWidgets.QAction(tb)
                action.setText(label)
                action.setIcon(resources.get_icon(runner_icon))
                action.triggered.connect(
                    lambda n=name, v=version, g=group_name: self._run(n, v, g)
                )
                action = tb.addAction(action)

    def _run(self, runner_name, version, group_name):
        self.session.cmds.SubprocessManager.run(
            runner_name, version, group_name
        )
        
    def receive_event(self, event_type, data):
        #print('!??? LauncerToolBar event', event_type, data)
        if event_type == 'subprocess_manager.runner_added':
            runner_name = data['runner_name']
            group_name = data['group_name']
            self.ensure_group(group_name)
            self.sync_group(group_name)

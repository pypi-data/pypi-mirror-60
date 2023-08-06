from kabaret.app import resources

from kabaret.app.ui.gui.widgets.widget_view import DockedView, QtWidgets, QtGui, QtCore


class SubprocessView(DockedView):
    def __init__(self, *args, **kwargs):
        super(SubprocessView, self).__init__(*args, **kwargs)

    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        label = QtWidgets.QLabel(main_parent)
        label.setText(
            """
<h1> Not Yet Implemented...</h1>
In an awesome future, you will see here a list of all processes running along
with their logged output and a few action to manage them.
<br>
In the meantime, enjoy the zen of python ;)
"""
        )

        lo = QtWidgets.QVBoxLayout()
        lo.addWidget(label)
        lo.addStretch(100)
        main_parent.setLayout(lo)

    def receive_event(self, event_type, data):
        pass

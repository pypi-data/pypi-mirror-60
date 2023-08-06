from AnyQt.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout

from Orange.widgets import gui
from Orange.widgets import settings
from Orange.widgets.widget import OWWidget, Input, Output
from orangecontrib.text.corpus import Corpus


class OWBaseVectorizer(OWWidget):
    """ A base class for feature extraction methods.

    Notes:
        Ensure that `create_configuration_layout` and `update_method` are overwritten.
    """
    # Input/output
    class Inputs:
        corpus = Input("Corpus", Corpus)

    class Outputs:
        corpus = Output("Corpus", Corpus)

    want_main_area = False
    resizing_enabled = False

    # Settings
    autocommit = settings.Setting(True)

    Method = NotImplemented

    def __init__(self):
        super().__init__()
        self.corpus = None
        self.method = None

        box = QGroupBox(title='Options')
        box.setLayout(self.create_configuration_layout())
        self.controlArea.layout().addWidget(box)

        buttons_layout = QHBoxLayout()
        buttons_layout.addSpacing(15)
        buttons_layout.addWidget(
            gui.auto_commit(None, self, 'autocommit', 'Commit', box=False)
        )
        self.controlArea.layout().addLayout(buttons_layout)
        self.update_method()

    @Inputs.corpus
    def set_data(self, data):
        self.corpus = data
        self.commit()

    def commit(self):
        self.apply()

    def apply(self):
        if self.corpus is not None:
            new_corpus = self.method.transform(self.corpus)
            self.Outputs.corpus.send(new_corpus)

    def update_method(self):
        self.method = self.Method()

    def on_change(self):
        self.update_method()
        self.commit()

    def send_report(self):
        self.report_items(self.method.report())

    def create_configuration_layout(self):
        return QVBoxLayout()

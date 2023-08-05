class InputData(object):

    def __init__(self, input_path, project, **kwargs):
        self.input_path = input_path
        self.project = project
        self.tasks = []
        self._create()

    def _create(self):
        raise NotImplementedError()


class JSONFileInputData(InputData):

    def _create(self):

from kivy.uix.progressbar import ProgressBar


class ConversionProgressBar(ProgressBar):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max = 100
        self.value = 0

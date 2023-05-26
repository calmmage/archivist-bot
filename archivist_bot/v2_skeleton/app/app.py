from calmlib import config_mixin
from calmlib.experimental.gpt_router import GptRouter

class App(config_mixin.ConfigMixin):
    # components:
    db: Database # todo: find where to import Database from
    gpt_router: GptRouter


    def __init__(self):
        pass


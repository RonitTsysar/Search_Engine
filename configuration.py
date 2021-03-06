class ConfigClass:
    def __init__(self):
        self.corpusPath = ''
        self.savedFileMainFolder = ''
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False

    def get__corpusPath(self):
        return self.corpusPath

    def set_corpusPath(self, path):
        self.corpusPath = path

    def get_toStem(self):
        return self.toStem

    def set_toStem(self, to_stem):
        self.toStem = to_stem

    def get_savedFileMainFolder(self):
        return self.savedFileMainFolder

    def set_savedFileMainFolder(self, path):
        self.savedFileMainFolder = path
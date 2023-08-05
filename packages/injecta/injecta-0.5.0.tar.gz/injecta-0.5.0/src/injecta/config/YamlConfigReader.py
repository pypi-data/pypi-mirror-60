from pathlib import Path
from injecta.config.ConfigPathsResolver import ConfigPathsResolver
from injecta.config.ConfigLoaderAndMerger import ConfigLoaderAndMerger
from injecta.config.ConfigReaderInterface import ConfigReaderInterface

class YamlConfigReader(ConfigReaderInterface):

    def __init__(self):
        self.__configPathsResolver = ConfigPathsResolver()
        self.__configLoaderAndMerger = ConfigLoaderAndMerger()

    def read(self, configPath: str):
        configPaths = self.__configPathsResolver.resolve(Path(configPath), Path(configPath).parent)

        return self.__configLoaderAndMerger.loadAndMerge(configPaths)

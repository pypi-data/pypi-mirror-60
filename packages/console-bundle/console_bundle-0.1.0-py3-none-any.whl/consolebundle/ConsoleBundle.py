import os
from typing import List
from injecta.bundle.Bundle import Bundle
from injecta.config.YamlConfigReader import YamlConfigReader
from injecta.definition.Definition import Definition
from injecta.bundle.definitionsPreparerFactory import create as createDefinitionsPreparer

class ConsoleBundle(Bundle):

    def __init__(self):
        self.__configReader = YamlConfigReader()
        self.__definitionsPreparer = createDefinitionsPreparer()

    def modifyDefinitions(self, definitions: List[Definition]):
        currentDir = os.path.dirname(os.path.abspath(__file__))
        config = self.__configReader.read(currentDir + '/_config/services.yaml')

        newDefinitions = self.__definitionsPreparer.prepare(config['services'])

        return definitions + newDefinitions

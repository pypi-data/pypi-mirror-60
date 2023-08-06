import dependency_injector.containers as containers
import dependency_injector.providers as providers


def fa():
# Defining dynamic container:
    container = containers.DynamicContainer()
    container.factory1 = providers.Factory(object)
    container.factory2 = providers.Factory(object)


def fb():
    container = containers.DynamicContainer()
    a = container.factory1()


fb()
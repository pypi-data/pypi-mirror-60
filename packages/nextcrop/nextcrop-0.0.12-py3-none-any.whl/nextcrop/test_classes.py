from dependency_injector import containers, providers


class A(object):
    name = 'class A'

    def __init__(self):
        print(self)


class B:
    name = 'class B'

    def __init__(self):
        print(self)


class D:
    def __init__(self, gui):
        print(f"D={gui.name}")


class Ca(containers.DeclarativeContainer):
    gui = providers.Singleton(A)


class Cb(containers.DeclarativeContainer):
    gui = providers.Singleton(B)


class C(containers.DeclarativeContainer):
    modes = providers.DependenciesContainer()
    d_factory = providers.Factory(D, gui=modes.gui)


def main():
    container = C(modes=Cb)
    d = container.d_factory()


main()

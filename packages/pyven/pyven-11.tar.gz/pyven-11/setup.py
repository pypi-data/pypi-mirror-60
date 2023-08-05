import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'pyven',
        version = '11',
        description = 'Management of PYTHONPATH for simultaneous dev of multiple projects',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/pyven',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['pyven', 'gclean', 'tasks', 'initopt', 'travis_ci', 'tests', 'release', 'runtests'],
        install_requires = ['twine', 'aridity'],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = ['pyven.py', 'gclean.py', 'tasks.py', 'initopt.py', 'foreignsyms', 'travis_ci.py', 'tests', 'release.py', 'pyven', 'runtests.py'])

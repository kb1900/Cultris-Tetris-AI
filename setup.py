from distutils.core import setup

setup(
    name='c2ai',
    version='0.0.3',
    author='kb1900',
    packages=['c2ai'],
    python_requires='>=3.6.0',
    install_requires=[
        'numpy',
        'matplotlib',
        'pandas',
        'scikit-learn',
        'Pillow',
        'scipy',
        'mss',
        'deap',
        'scoop',
        'pathos',
        'statistics',
        'dill',
        'pyautogui'
    ]
)

from setuptools import setup

setup(
    name="pymodore",
    version="1.0.2",
    author="Natan 'Albrigs' Fernandes dos Santos",
    author_email="natanfs013@gmail.com",
    py_modules=['pymodore'],
    description='A simple terminal pomodore timer.',
    url='https://github.com/NatanFernandesSantos/pymodore',
    license='GNU 3.0',
    keywords=['pomodoro','console','profit', 'command', 'line', 'timer'],
    python_requires='>=3',
    install_requires=[
        'Click',
        'termcolor',
        'python-vlc',
    ],
    entry_points='''
        [console_scripts]
        pymodore=pymodore:pomodoro
    ''',

)

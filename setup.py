from setuptools import setup


setup(
    name = 'dcc',
    install_requires = [
        'pyramid',
        'pyramid_handlers',
        'waitress',
        'sqlalchemy',
        'pyramid_tm',
        'zope.sqlalchemy',
        'pyramid_mako',
    ],
    entry_points="""\
        [paste.app_factory]
            main = app:main
""",
)


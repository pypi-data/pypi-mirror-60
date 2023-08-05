
SETUP_INFO = dict(
    name = 'infi.datatable',
    version = '0.5',
    author = 'Itai Shirav',
    author_email = 'itais@infinidat.com',

    url = 'https://git.infinidat.com/host-opensource/infi.datatable',
    license = 'BSD',
    description = """This project provides Backbone/Bootstrap components for displaying Infinidat-style collections""",
    long_description = """This project provides Backbone/Bootstrap components for displaying Infinidat-style collections. It uses the server's REST API for sorting and pagination.""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['setuptools'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': [
'*.css',
'*.html',
'*.js'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()


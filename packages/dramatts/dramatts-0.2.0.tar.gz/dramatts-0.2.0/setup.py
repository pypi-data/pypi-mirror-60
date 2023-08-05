from setuptools import setup, find_packages

# fetch readme for pypi
with open('README.rst', 'r') as file:
    readme = file.read()

name = 'dramatts'
install_requires = [
    'PyQt5',
    'setuptools_scm',
    'jinja2',
    'pytest'
]

license = 'GPL3'
summary = "Screen play / drama text to multi-voice audio play converter"
git_source = "https://gitlab.com/thecker/dramatts/"
doc_url = "https://gitlab.com/thecker/dramatts/blob/master/README.rst"
home = git_source

setup(
    name=name,
    # version=version,
    packages=find_packages(),

    include_package_data=True,

    use_scm_version=True,
    setup_requires=['setuptools_scm'],

    install_requires=install_requires,
    python_requires='>=3',

    package_data={
        'examples': ['*.json', '*.txt']
    },

    # metadata to display on PyPI
    author="Thies Hecker",
    author_email="thies.hecker@gmx.de",
    description=summary,
    long_description=readme,
    long_description_content_type='text/x-rst',
    license=license,
    keywords="TTS play text-to-speech festival audio book",
    url=home,
    project_urls={
        "Documentation": doc_url,
        "Source Code": git_source,
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ]
)

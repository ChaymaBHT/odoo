import setuptools
from apps.__about__ import __version__

# To install the module launche
# pip install -e ./invoke-runbot

long_description = ''
# with open("README.md", "r", encoding="utf-8") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="invoke-runbot",
    version=__version__,
    author="Eezee-It",
    author_email="admin@eezee-it.com",
    description="Eezee-It Runbot command line tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/eezee-it/invoke-runbot/",
    install_requires=[
        'invoke',
        'colorama',
        'pylxd',
        'tabulate',
        'humanize',
        'slug',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'runbot = apps.main:program.run',
            'runbotmgr = apps.main:program_manager.run',
        ]
    }
)

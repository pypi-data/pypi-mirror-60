import setuptools

INSTALL_REQUIRES = [
    'pynwb',
    'hdmf',
    'pandas',
    'networkx',
    'matplotlib',
    'numpy',
    'scipy',
    'python-dateutil',
    'python-intervals',
    'franklab_nwb_extensions'
]
TESTS_REQUIRE = ['pytest >= 2.7.1']
DESCRIPTION = "Convert files from Loren Frank Lab old matlab format to NWB 2.0"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="filterframework_to_nwb",
    version="0.1.0.dev0",
    author="Frank Lab members",
    author_email="loren@phy.ucsf.edu",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LorenFrankLab/filterframework_to_nwb",
    packages=setuptools.find_packages(),
    package_data={'filterframework_to_nwb': ["*.yaml"]},
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.6',
    tests_require=TESTS_REQUIRE,
    entry_points='''
        [console_scripts]
        create_franklab_spec=filterframework_to_nwb.create_franklab_spec:main
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

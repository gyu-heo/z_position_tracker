import pathlib
from setuptools import find_packages, setup

# # The directory containing this file
# HERE = pathlib.Path(__file__).parent

# # The text of the README file
# README = (HERE / "README.md").read_text()

VERSION = "0.2.2"

# This call to setup() does all the work
setup(
    name="your_env",
    version=VERSION,
    description="your_code_description",
    # long_description=README,
    # long_description_content_type="text/markdown",
    url="your_github_repo",
    # license="LGPLv2+",
    # classifiers=[
    #     "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.6",
    #     "Programming Language :: Python :: 3.7",
    #     "Programming Language :: Python :: 3.8",
    # ],
    packages=find_packages(exclude=['use_cases', 'use_cases.*']),
    include_package_data=True,
    install_requires=["numpy", "torch", "scipy", "argparse"],
    scripts=[
        "module/multi_process.sh",
        "module/single_process.sh",
    ],
    entry_points={
        "console_scripts": [
            "multi_process = module.multi_process:multi_process",
            "single_process = module.multi_process:single_process",
        ]
    },
)
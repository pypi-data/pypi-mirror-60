import setuptools
import subprocess


def get_head_tag():
    return subprocess.check_output(
        ["git", "tag", "--points-at", "HEAD"]
    ).strip().decode("utf-8")


setuptools.setup(name="pylars",
                 version=get_head_tag(),
                 packages=setuptools.find_packages(),
                 python_requires=">=3.6",
                 install_requires=[
                     "pandas>=1.0.0",
                 ])

import setuptools

with open("README.md", "r") as readme:
    longDescription = readme.read()

setuptools.setup(
    name="mulang",
    version="0.0.3",
    author="无名",
    author_email="mulanrevive@gmail.com",
    entry_points = {
        "console_scripts": ['ulang = ulang.runtime.main:main']
        },
    description="描述",
    long_description=longDescription,
    long_description_content_type="text/markdown",
    url="https://github.com/MulanRevive/mulan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)
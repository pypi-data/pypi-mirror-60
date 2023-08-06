from setuptools import setup

# with open("requirements.txt") as f:
#     install_requires = filter(lambda line: line != "", f.read().split("\n"))

setup(
    name="gg69-super-calc-engine",
    description="One line calculator engine with example of wrapping his functional",
    long_description="",
    keywords=["cool", "calc", "expeval", "calculator", "69"],
    author="Andreew Gregory",
    author_email="grinadand@gmail.com",
    url="https://github.com/1Gregory/gg69-calc-engine.git",
    download_url="https://github.com/1Gregory/gg69-calc-engine/archive/1.0.tar.gz",
    version="1.1",
    install_requires=[
        "colorama"
    ],
    packages=["gg69_expeval"],
    license="MIT",
)

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qzone_api",
    version="0.0.3",
    author="Huan Xin",
    author_email="mc.xiaolang@foxmail.com",
    description="QQ空间API封装",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huanxin996/qzone_api",
    packages=setuptools.find_packages(),
    install_requires=['aiohttp>=3.11.11','lxml>=5.3.0','loguru>=0.7.3'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
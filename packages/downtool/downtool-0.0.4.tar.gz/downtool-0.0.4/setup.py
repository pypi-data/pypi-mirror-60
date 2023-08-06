import setuptools


setuptools.setup(
    name="downtool", 
    version="0.0.4",
    author="chen zhihan&xu chengbo",
    license='MIT Licence',
    author_email="im.czh@qq.com",
    description="a downtool for everyone who want to have a good experience with Crawling every image wanted.",
    long_description="a downtool for everyone who want to have a good experience with Crawling every image wanted.",
    long_description_content_type="text/markdown",
    url="https://github.com/czhmisaka/downtool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests','os','fake_useragent','datetime','threading'],
    python_requires='>=3.6',
) 
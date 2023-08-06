from setuptools import setup, find_packages

setup(
    name="pyddi_xupan",
    version="0.0.1",
    keywords=["pip", "omicsDI", "WS-client"],
    py_modules=["pyddi_xupan"],
    description="web-service client of omicsDI API",
    license="MIT Licence",
    url="https://github.com/OmicsDI/Pyddi",
    author="Xpon",
    author_email="hll3939092@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["requests"]
)

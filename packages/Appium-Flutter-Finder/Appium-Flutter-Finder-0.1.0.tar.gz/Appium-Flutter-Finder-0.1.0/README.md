# Getting the Appium Flutter Finder

There are three ways to install and use the Appium Flutter Finder.

1. Install from [PyPi](https://pypi.org), as ['Appium-Flutter-Finder'](https://pypi.org/project/Appium-Flutter-Finder/).

    ```shell
    pip install Appium-Flutter-Finder
    ```

2. Install from source, via [PyPi](https://pypi.org). From ['Appium-Flutter-Finder'](https://pypi.org/project/Appium-Flutter-Finder/),
download and unarchive the source tarball (Appium-Flutter-Finder-X.X.tar.gz).

    ```shell
    tar -xvf Appium-Flutter-Finder-X.X.tar.gz
    cd Appium-Flutter-Finder-X.X
    python setup.py install
    ```

3. Install from source via [GitHub](https://github.com/appium/python-client).

    ```shell
    git clone git@github.com:appium/python-client.git
    cd python-client
    python setup.py install
    ```

# release

```
pip install twine
```

```
python setup.py sdist
twine upload dist/Appium-Flutter-Finder-0.1.0.tar.gz
```
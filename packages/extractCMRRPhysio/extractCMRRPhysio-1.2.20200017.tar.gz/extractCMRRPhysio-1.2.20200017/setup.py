import setuptools

from extractCMRRPhysio import version

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = version.__version__

setuptools.setup(name='extractCMRRPhysio',
                 version=VERSION,
                 description='extractCMRRPhysio.m(https://github.com/CMRR-C2P/MB/blob/master/extractCMRRPhysio.m) in Python',
                 author='YingLi Lu',
                 author_email='yinglilu@gmail.com',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/yinglilu/extractCMRRPhysio_github_actions",
                 license='MIT',
                 entry_points={
                     'console_scripts': [
                         'extractCMRRPhysio = extractCMRRPhysio.main:run']},
                 packages=setuptools.find_packages(),
                 # install_requires=['pytest,pydicom'],
                 install_requires=[
                     'pytest',
                     'pydicom',
                 ],
                 python_requires='>=3.6',
                 zip_safe=True,
                )

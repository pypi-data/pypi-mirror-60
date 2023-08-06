from setuptools import setup, find_packages

setup(name='filenuke',
      version='0.0.0',
      description='Securely erase files or directories as much as possible from userspace',
      author='Kevin Froman',
      author_email='beardog@mailbox.org',
      url='https://chaoswebs.net/',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires=[],
      python_requires='>=3.6',
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
      ],
     )

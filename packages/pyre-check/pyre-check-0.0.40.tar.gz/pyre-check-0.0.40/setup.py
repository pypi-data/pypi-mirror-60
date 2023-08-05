import glob
import json
import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    sys.exit('Error: pyre-check only runs on Python 3.5 and above.')

def get_all_stubs(root: str):
    if not os.path.isdir(root):
        return []
    result = []
    for absolute_directory, _, _ in os.walk(root):
        relative_directory, files = get_data_files(
            directory=absolute_directory, extension_glob="*.pyi"
        )
        if not files:
            continue
        target = os.path.join("lib", "pyre_check", relative_directory)
        result.append((target, files))
    return result

def get_data_files(directory: str, extension_glob: str):
  # We need to relativize data_files, see https://github.com/pypa/wheel/issues/92.
  relative_directory = os.path.relpath(os.path.abspath(directory), "/var/folders/v_/xp6bmm0j3c7_3zkf8nm3rnysdbprsf/T/tmp.kcDvZQg2")
  return (
      relative_directory,
      glob.glob(os.path.join(relative_directory, extension_glob)),
  )

def find_taint_stubs():
    _, taint_stubs = get_data_files(
        directory=os.path.join("/var/folders/v_/xp6bmm0j3c7_3zkf8nm3rnysdbprsf/T/tmp.kcDvZQg2", "taint"), extension_glob="*"
    )
    _, third_party_taint_stubs = get_data_files(
        directory=os.path.join("/var/folders/v_/xp6bmm0j3c7_3zkf8nm3rnysdbprsf/T/tmp.kcDvZQg2", "third_party_taint"), extension_glob="*"
    )
    taint_stubs += third_party_taint_stubs
    if not taint_stubs:
        return []
    return [(os.path.join("lib", "pyre_check", "taint"), taint_stubs)]


with open('README.md') as f:
    long_description = f.read()


setup(
    name='pyre-check',
    version='0.0.40',
    description='A performant type checker for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://pyre-check.org/',
    download_url='https://github.com/facebook/pyre-check',
    author='Facebook',
    author_email='pyre@fb.com',
    maintainer='Facebook',
    maintainer_email='pyre@fb.com',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    keywords='typechecker development',

    packages=find_packages(exclude=['tests', 'pyre-check']),
    data_files=[('bin', ['bin/pyre.bin'])]
    + get_all_stubs("/var/folders/v_/xp6bmm0j3c7_3zkf8nm3rnysdbprsf/T/tmp.kcDvZQg2/typeshed")
    + get_all_stubs("/var/folders/v_/xp6bmm0j3c7_3zkf8nm3rnysdbprsf/T/tmp.kcDvZQg2/stubs/django")
    + get_all_stubs("/var/folders/v_/xp6bmm0j3c7_3zkf8nm3rnysdbprsf/T/tmp.kcDvZQg2/stubs/lxml")
    + find_taint_stubs(),
    python_requires='>=3.5',
    install_requires=['pywatchman', 'psutil', 'libcst', 'pyre_extensions'],
    extras_require={
      "sapp": ["click", "click-log", "ipython==7.6.1", "munch", "pygments", "SQLAlchemy", "ujson~=1.35", "xxhash~=1.3.0", "prompt-toolkit~=2.0.9"]
    },
    entry_points={
        'console_scripts': [
            'pyre = pyre_check.client.pyre:main',
            'pyre-upgrade = pyre_check.tools.upgrade.upgrade:main',
            'sapp = pyre_check.tools.sapp.sapp.cli:cli [sapp]',
        ],
    }
)

from setuptools import setup

INSTALL_REQUIRES = [
    'requests'
]

setup(
    use_scm_version={"write_to": "organizze_client/_version.py"},
    setup_requires=["setuptools-scm", "wheel", "setuptools>=40.0"],
    # package_dir={"": "organizze_client"},
    install_requires=INSTALL_REQUIRES,
)

from setuptools import setup, find_packages

setup(
    name="retrofy",
    author="Bernardo Coutinho Galvão dos Santos",
    author_email="bgalvaods@gmail.com",
    license="MIT",
    version = "0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["numpy", "requests", "Pillow", "blend_modes"]
)

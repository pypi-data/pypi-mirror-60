from setuptools import setup, find_packages

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('--')) and (";" not in line)]

setup(
    name="jinja2_getenv_extension",
    version="0.0.2",
    license="BSD",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires='>=3.0',
    description="a jinja2 extension to access to system environment variables",
    url="https://github.com/metwork-framework/jinja2_getenv_extension",
    keywords="jinja2 extension",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3"
    ]
)

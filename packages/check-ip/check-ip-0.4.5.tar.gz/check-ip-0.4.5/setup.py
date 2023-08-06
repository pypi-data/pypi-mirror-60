from setuptools import find_packages
from setuptools import setup

with open("README.md") as f:
    README = f.read()

setup(
    name="check-ip",
    version="0.4.5",
    description="Check your public IP address and update DNS records on Cloudflare.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Samuel Searles-Bryant",
    author_email="devel@samueljsb.co.uk",
    license="MIT",
    url="https://github.com/samueljsb/check-ip/",
    packages=find_packages(),
    install_requires=["click", "cloudflare", "pyyaml", "requests"],
    entry_points={"console_scripts": ["check-ip=check_ip.cli:main"]},
)

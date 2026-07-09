from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="kirana_ledger",
    version="1.0.0",
    description="Hyper-Local Inventory + Udhaar Ledger for Kirana Shops",
    author="Kirana Tech",
    author_email="dev@kirana-ledger.example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)

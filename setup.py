from setuptools import find_namespace_packages, setup, find_packages

setup(
    name="mllama",
    version="0.1",
    packages=find_packages(where="src") + find_packages(where="vendor/mlx-engine"),
    package_dir={"": "src", "mlx_engine": "vendor/mlx-engine/mlx_engine"},
)

from setuptools import setup

setup(
    name="Qactuar",
    version="0.0.0",
    description="ASGI compliant web server",
    long_description="ASGI compliant web server",
    long_description_content_type="text/markdown",
    author="Anthony Post",
    author_email="postanthony3000@gmail.com",
    license="MIT License",
    url="https://github.com/Ayehavgunne/Qactuar/",
    packages=["qactuar"],
    install_requires=[],
    extras_require={"dev": ["mypy", "black", "isort"]},
    python_requires=">=3.7",
)

import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="initpyproj",
    version="1.0.0",
    author="Nils Urbach",
    author_email="ndu01u@gmail.com",
    description="Initialize an empty python project; make it a git repo; and sync it with a new GitHub repo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=[],
    url="https://github.com/Schnilsibus/initpyproj",
    package_dir={"": "_core"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python"
    ],
    test_suite="tests",
    package_data={"templates": ["[template]*"]}
)

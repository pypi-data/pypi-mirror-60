from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Ichlasul Affan",
    author_email="ichlasul.affan@ui.ac.id",
    classifiers=[
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
    ],
    message_extractors = {
        'csui-git-wrapper': [('**.py', 'python', None),],
    },
    description="csui-git-wrapper wraps Git commands to submit and pull problems for elementary programming courses. This package is currently only intended for usage inside Faculty of Computer Science, Universitas Indonesia.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["requests"],
    keywords=["git wrapper", "fasilkom ui"],
    name="csui-git-wrapper",
    python_requires=">=3.6",
    license="MIT",
    packages=["csui_git_wrapper"],
    url="https://gitlab.cs.ui.ac.id/ichlasul.affan/csui-git-wrapper",
    entry_points={
        "console_scripts": ["csuisubmit=csui_git_wrapper.__main__:main"]
    },
    version="0.0.3",
    include_package_data=True
)

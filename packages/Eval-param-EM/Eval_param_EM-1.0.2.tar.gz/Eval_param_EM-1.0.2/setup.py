from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="Eval_param_EM",
    version="1.0.2",
    description="A Python package to evaluate the regression and classification models.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    #url="https://github.com/Eshikamahajan/Evaluation-Parameters-for-ML-models",
    author="Eshika Mahajan",
    author_email="eshikamahajan21@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["Eval_param_EM"],
    include_package_data=True,
    install_requires=["requests==2.0.1"],
    entry_points={
        "console_scripts": [
            "Eval_Eshika=Eval_param_EM",
        ]
    },
)

from setuptools import setup, find_packages

setup(
    name="rubber-duck-assistant",
    version="0.1.0",
    description="Asystent głosowy dla programistów inspirowany metodą gumowej kaczuszki",
    author="RubberDuck Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "pyaudio>=0.2.14",
        "pynput>=1.7.6",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rubber-duck=main:main",
        ],
    },
)

from setuptools import setup



setup(
    name="topsis-101703445",
    version="1.0.1",
    description="A python package implementing topsis",
    long_description="Project 1 of UCS633 Ritwik Khurana 101703445",
  
    author="Ritwik Khurana",
    
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_101703445"],
    include_package_data=True,
    
    entry_points={
        "console_scripts": [
            "topsis-101703445=topsis_101703445.cli:main",
        ]
    },
)

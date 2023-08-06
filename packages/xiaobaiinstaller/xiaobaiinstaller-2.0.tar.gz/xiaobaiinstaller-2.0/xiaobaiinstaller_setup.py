import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="xiaobaiinstaller", # Replace with your own username
    version="2.0",
    author="Tser",
    author_email="807447312@qq.com",
    description="Xiaobai Test Tools Install",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/big_touch/xiaobaiinstaller",
    packages=setuptools.find_packages(),
    keywords="xiaobai tool test install",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    py_modules=['xiaobaiinstaller'],
    install_requires=[
    	"requests_html"
    ],
    package_data={
        'xiaobaiinstaller': ['xiaobaicore.cp38-win_amd64.pyd', 'logo.ico'],
    },
    entry_points={'console_scripts': [
        'xiaobaiinstaller = xiaobaiinstaller.installer:main',
    ]},
)


#python setup.py sdist bdist_wheel

#python -m twine upload dist/*
import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()
    

setuptools.setup(
    name="starmf_proxy", # Replace with your own username
        version="0.0.2",
        author="Vijay",
        author_email="vijayamadhavareddy@gmail.com",
        description="Starmf Proxy Package",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://gitlab.com/thinkmf/starve_proxy",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
)
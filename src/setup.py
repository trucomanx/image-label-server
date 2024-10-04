from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8");

setup(
    name="image-label-server",
    version="0.1.0",
    description='A server and client for labeling in datasets',
    author='Fernando Pujaico Rivera',
    author_email='fernando.pujaico.rivera@gmail.com',
    maintainer='Fernando Pujaico Rivera',
    maintainer_email='fernando.pujaico.rivera@gmail.com',
    url='https://github.com/trucomanx/image-label-server',
    keywords="labeling, dataset, server",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    packages=find_packages(),
    install_requires=[
        "Flask",
        "requests",
        "pillow"
    ],
    entry_points={
        'console_scripts': [
            'image-label-server=image_label_server.server:main',
            'image-label-client=image_label_server.client:main',
            'image-label-export-csv=image_label_server.export_csv:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    project_urls={  # Optional
        "Bug Reports": "https://github.com/trucomanx/image-label-server/issues",
        "Funding": "https://trucomanx.github.io/en/funding.html",
        "Source": "https://github.com/trucomanx/image-label-server/",
    },
)


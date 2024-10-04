from setuptools import setup, find_packages

setup(
    name="image-label-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "requests",
        "Werkzeug",
    ],
    entry_points={
        'console_scripts': [
            'image-label-server=image_label_server.server:main',
            'image-label-client=image_label_server.client:main',
            'image-label-export-csv=image_label_server.export_csv:main',
        ],
    },
)


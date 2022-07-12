from setuptools import setup

setup(
    name="rss_reader",
    version="4.3",
    author="Alena Kniazeva",
    author_email="elena.n.kniazeva@gmail.com",
    description="RSS-reader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    'fpdf>=1.7.2',
    'requests>=2.26.0',
    'lxml>=4.9.0',
    'beautifulsoup4>=4.11.1',
    'jsonlines>=3.0.0',
    'python-dateutil>=2.8.2'
    ],
    entry_points={
        'console_scripts': [
            'rss_reader = rss_reader:main',
        ],
    }
)
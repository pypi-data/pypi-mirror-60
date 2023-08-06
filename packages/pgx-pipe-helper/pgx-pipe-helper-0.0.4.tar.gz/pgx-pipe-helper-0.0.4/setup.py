from setuptools import setup
setup(
    name="pgx-pipe-helper",
    version="0.0.4",
    description="Simple helper for common functionality",
    author="Guy Allard, LUMC",
    author_email="guyallard01@gmail.com",
    url="https://github.com/lumc/pgx-pipe-helper",
    platforms=['any'],
    packages=["pipe_helper"],
    install_requires=[
        "pyyaml",
        "locus_processing",
        "snakemake",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
    ],
    keywords = 'bioinformatics snakemake'
)

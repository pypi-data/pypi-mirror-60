import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twitch-chest-bot",
    version="0.9.1",
    author="J4CK VVH173",
    author_email="author@example.com",
    description="Twitch bot for auto collection of chests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/J4CKVVH173/twitch_auto_chests",
    packages=setuptools.find_packages(),
    install_requires=[
            'daemon-process',
            'numpy==1.18.1',
            'pynput==1.6.6',
            'pyscreenshot==0.6',
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
)

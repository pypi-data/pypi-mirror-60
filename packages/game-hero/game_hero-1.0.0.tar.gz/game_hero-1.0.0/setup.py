import setuptools

with open("README.md", "r") as readme_file:
    project_description = readme_file.read()

setuptools.setup(
    name="game_hero",
    version="1.0.0",
    author="Alexandru Sandu",
    author_email="sandualex7@gmail.com",
    description="A HeroGame implemented for demonstration purposes",
    long_description=project_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandu-alexandru/hero_game/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
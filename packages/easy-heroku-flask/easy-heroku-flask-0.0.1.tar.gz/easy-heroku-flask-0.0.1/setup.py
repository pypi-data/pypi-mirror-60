import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name = "easy-heroku-flask",
  version = "0.0.1",
  author = "Casey Johnson",
  author_email = "caseyjohnsonwv@gmail.com",
  description = "Create new Heroku/Flask file structures in one command.",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = "https://github.com/caseyjohnsonwv/easy-heroku-flask",
  packages = setuptools.find_packages(),
  include_package_data = True,
  scripts = ["bin/easy-heroku-flask"],
  install_requires = [],
)

# easy-heroku-flask
For quickly generating Heroku/Flask projects with populated application templates. Currently supports SQLAlchemy.

## Output
```sh
project
├── app.py
├── .env
├── env.py
├── .git
│   └── ...
├── .gitignore
├── LICENSE
├── Procfile
├── README.md
├── requirements.txt
├── static
│   ├── index.css
│   └── index.js
└── templates
    └── index.html
```

## Installation
To install easy-heroku-flask:

`$ python3 -m pip install easy-heroku-flask`

To update easy-herkou-flask:

`$ python3 -m pip install easy-heroku-flask --upgrade`

## Usage
To create a new Heroku/Flask project:

`$ easy-heroku-flask -n <project name>`

### Required Arguments

| Flag | Name | Description |
|:----:|--------|-------------|
| -n | --project-name | Name of new project folder to create. |

### Optional Arguments

| Flag | Name | Description |
|:----:|--------|-------------|
| -h | --help | Display help text. |
| -u | --repo-url | URL of an empty remote repository. The project template will be pushed to *origin/master*. |


## Authors
- Casey Johnson - *initial work* - <a href="https://github.com/caseyjohnsonwv">caseyjohnsonwv</a>

## License
This project is licensed under the MIT License. See <a href="https://github.com/caseyjohnsonwv/easy-heroku-flask/blob/master/LICENSE">LICENSE</a> for details.

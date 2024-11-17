banner() {
    printf "\n\e[37;44m $1 \e[0m\n"
}

banner "Pylint"
pylint main.py

banner "MyPy"
mypy main.py

banner "Pyflakes"
pyflakes main.py

banner "PyCodeStyle"
pycodestyle main.py

banner "Bandit"
bandit main.py

banner "Radon"
radon cc -a main.py

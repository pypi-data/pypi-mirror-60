# Contributing

Contributions are welcome, and they are greatly appreciated\! Every
little bit helps, and credit will always be given.

## Bug reports

When [reporting a
bug](https://%7B%7B%20cookiecutter.git_base%20%7D%7D/%7B%7B%20cookiecutter.git_group%20%7D%7D/%7B%7B%20cookiecutter.repo_name%20%7D%7D/issues)
please include:

>   - Your operating system name and version.
>   - Any details about your local setup that might be helpful in
>     troubleshooting.
>   - Detailed steps to reproduce the bug.

## Documentation improvements

subsample_fastas could always use more documentation,
whether as part of the official subsample_fastas docs,
in docstrings, or even on the web in blog posts, articles, and such.

## Feature requests and feedback

The best way to send feedback is to file an issue at
<>https://gitlab.inria.fr/>pleiade/python-subsample_fastas/issues.

If you are proposing a feature:

  - Explain in detail how it would work.
  - Keep the scope as narrow as possible, to make it easier to
    implement.

## Development

To set up <span class="title-ref">python-subsample_fastas</span>
for local development:

1.  Fork [python-subsample_fastas](https://%7B%7B%20cookiecutter.git_base%20%7D%7D/%7B%7B%20cookiecutter.git_group%20%7D%7D/%7B%7B%20cookiecutter.repo_name%20%7D%7D/forks/)
    (look for the "Fork" button).

2.  Clone your fork
        locally:
    
        git clone git@gitlab.inria.fr:your_name_here/python-subsample_fastas.git

3.  Create a branch for local development:
    
        git checkout -b name-of-your-bugfix-or-feature
    
    Now you can make your changes locally.

4.  When you're done making changes, run all the checks, doc builder and
    spell checker with
    [tox](http://tox.readthedocs.io/en/latest/install.html) one command:
    
        tox

5.  Commit your changes and push your branch to GitHub:
    
        git add .
        git commit -m "Your detailed description of your changes."
        git push origin name-of-your-bugfix-or-feature

6.  Submit a pull request through the GitHub website.

### Pull Request Guidelines

If you need some code review or feedback while you're developing the
code just make the pull request.

For merging, you should:

1.  Include passing tests (run `tox`)\[1\].
2.  Update documentation when there's new API, functionality etc.
3.  Add a note to `CHANGELOG.md` about the changes.
4.  Add yourself to `AUTHORS.md`.

### Tips

To run a subset of tests:

    tox -e envname -- pytest -k test_myfeature

To run all the test environments in *parallel* (you need to `pip install
detox`):

    detox

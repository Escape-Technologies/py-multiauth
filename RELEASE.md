In order to publish a new release, after commiting the changes to main and updating the `pyproject.toml` version, run the following commands:

```bash
git tag "v$(poetry version -s)"
git push origin "v$(poetry version -s)"
```
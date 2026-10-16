# GumBow

A Git-backed catalog of reusable GUM libraries. This initial catalog accompanies
[the package-management implementation](https://github.com/SteveWaggoner/GumLang/pull/85).
It is a test repository; target support in the catalog is declared, not certified.

GUM downloads a small index and selected `.gum.pack` archives over HTTP, rather
than cloning this repository. The archive contains full backend-neutral ASTs,
including private implementations, metadata and required native assets.

## Try the example

With GUM 0.1.9 or the companion PR installed, the default repository is GumBow. To test an unmerged catalog, replace its
configuration using `--ref BRANCH_OR_COMMIT`:

```sh
gum package repo remove gumbow
gum package repo add gumbow https://github.com/SteveWaggoner/GumBow --ref BRANCH_OR_COMMIT
gum package search example --target node
```

In a GUM project:

```gum
import gumbow.example.{answer}

def main() { print(answer()) }
```

```sh
gum check --target node --add-dependencies
gum run --target node
```

The app prints `42`. Check records an exact dependency and a per-target lock;
subsequent projects share the downloaded archive through GUM's global cache.

## Layout and publishing

- `examples/hello/`: source project for `gumbow.example` 1.0.0.
- `packages/<server-account-repository>/<namespace>/*.gum.pack`: immutable archives.
- `index/latest.json`: current catalog location and full SHA-256.
- `index/<revision>/packages.db`: SQLite metadata and indexed target membership.

From a library project, `gum package publish --repo gumbow` creates a branch and
draft pull request. A changed package requires a new version. All identifiers are
lowercase; this repository's author identity is `github.com-stevewaggoner-gumbow`.

Run `python tools/validate_catalog.py` to verify the catalog, target index,
archive hashes and every archived file. This validation uses only Python's
standard library and does not require access to the private compiler repository.

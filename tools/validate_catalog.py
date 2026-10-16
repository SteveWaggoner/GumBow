"""Validate the catalog and archives using Python's standard library only."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sqlite3
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    assert not path.is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')), name
    assert '\\' not in name and ':' not in name, name
    return ROOT.joinpath(*path.parts)


def main():
    pointer = json.loads((ROOT / 'index/latest.json').read_text())
    assert pointer['format'] == 1
    database = safe(pointer['path'])
    assert digest(database.read_bytes()) == pointer['sha256'] == pointer['revision']
    connection = sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True)
    connection.execute('PRAGMA trusted_schema=OFF')
    assert connection.execute('PRAGMA integrity_check').fetchone() == ('ok',)
    rows = connection.execute('SELECT id, author, namespace, version, metadata FROM packages').fetchall()
    for package_id, author, namespace, version, metadata in rows:
        row = json.loads(metadata)
        assert (author, namespace, version) == (row['author'], row['namespace'], row['version'])
        assert author == author.lower() and namespace == namespace.lower()
        indexed = {r[0] for r in connection.execute('SELECT target FROM targets WHERE package_id=?', (package_id,))}
        assert indexed == set(row['targets'])
        archive = safe(row['archive'])
        assert digest(archive.read_bytes()) == row['sha256']
        with zipfile.ZipFile(archive) as package:
            names = package.namelist()
            assert len(names) == len({n.casefold() for n in names})
            for name in names:
                safe(name)
            manifest = json.loads(package.read('package.json'))
            for key in ('author', 'namespace', 'version', 'targets', 'units', 'dependencies'):
                assert manifest[key] == row[key], key
            assert set(names) == {'package.json', *manifest['files']}
            for name, sha in manifest['files'].items():
                assert digest(package.read(name)) == sha, name
        print(f'{author}/{namespace} {version}: archive and catalog OK')
    connection.close()
    assert rows, 'Catalog is empty'


if __name__ == '__main__':
    main()

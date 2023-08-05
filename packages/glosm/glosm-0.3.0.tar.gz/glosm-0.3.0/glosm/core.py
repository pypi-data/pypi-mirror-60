"""Core API."""

import os
import json

from typing import Dict, Union, List, Tuple
from functools import lru_cache


DEFAULT_PATH_SECRETS_FILE = "~/.glosm.json"


Secrets = Union[Dict[str, "Secrets"], List["Secrets"], str]
Path = Union[List[str], Tuple[str], str]


@lru_cache(maxsize=128)
def _secrets(path_secrets_file: str = None) -> Dict:

    with open(os.path.expanduser(path_secrets_file or DEFAULT_PATH_SECRETS_FILE), "r") as f:
        return json.load(f)


def _dereferenced(secrets: Secrets, secrets_path: Path = None) -> Secrets:
    """Returns dereferenced secrets.

    A reference to a glosm secret is a list of two or more elements, with first element being the sentinel, representing
    the root of glosm. For example, if sentinel value is "$glosm" then a valid glosm reference is
    `["$glosm", "accounts", "joe"]` and it will be dereferenced by calling `get("accounts", "joe"). Dereferenced values
    may themselves contain glosm references, e.g. turtles all the way down.

    Glosm references help avoid repetition.

    Secrets are dereferenced recursively. Circular references are possible because we do not check for their presence
    because they are meaningless and we assume users will not make this mistake. Dereferencing circular values will
    crash glosm with `RunTimeError`.

    Glosm may also crash with deeply nested references because this function is recursive and Python limits recursion
    depth.
    """
    secrets_path = secrets_path or []

    glosm_path_sentinel = "$glosm"

    if isinstance(secrets, dict) and len(secrets) > 0:
        for k in secrets:
            secrets[k] = _dereferenced(secrets=secrets[k], secrets_path=secrets_path + [k])

    if isinstance(secrets, list) and len(secrets) > 0:

        if secrets[0] == glosm_path_sentinel:
            referenced_path = secrets[1:]

            if referenced_path == secrets_path[0 : len(referenced_path)]:
                # reference_path may not be ancestor of secrets_path and it may not be same as secrets_path
                raise ValueError(
                    (
                        f"Detected circular reference: secret in path {secrets_path} ",
                        "references secret in {referenced_path}.",
                    )
                )

            secrets = get(*referenced_path)
            secrets = _dereferenced(secrets=secrets, secrets_path=secrets_path)
        else:
            secrets = [_dereferenced(secrets=s, secrets_path=secrets_path) for s in secrets]

    return secrets


def get(*path: Path) -> Secrets:
    """Get a secret, specified by one or more keys. Without any keys, return all secrets.

    The keys are traversed recursively. If `get()` returns `{1: {2: {3: 4}}}` then `get(1, 2, 3)` will return `4`.
    """

    all_secrets = _secrets()

    if not path:
        return all_secrets

    secrets = all_secrets
    for key in path:
        secrets = secrets[key]

    secrets = _dereferenced(secrets=secrets, secrets_path=list(path))
    return secrets

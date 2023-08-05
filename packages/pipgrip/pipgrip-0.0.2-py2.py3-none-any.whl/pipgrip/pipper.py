import logging
import os
import re
import subprocess
import sys

import pkg_resources
from packaging.markers import default_environment
from packaging.utils import canonicalize_name
from pkginfo import get_metadata

from pipgrip.compat import PIP_VERSION, urlparse

logger = logging.getLogger(__name__)


def parse_req(requirement):
    if requirement.startswith("."):
        req = pkg_resources.Requirement.parse(requirement.replace(".", "rubbish", 1))
        req.key = "."
        full_str = req.__str__().replace(req.name, req.key)
    else:
        req = pkg_resources.Requirement.parse(requirement)
        req.key = canonicalize_name(req.key)
        req.name = req.key
        full_str = req.__str__()  # .replace(req.name, req.key)

    def __str__():
        return full_str

    req.__str__ = __str__
    return req


def _get_wheel_args(index_url, extra_index_url, pre, cache_dir=None):
    args = [
        sys.executable,
        "-m",
        "pip",
        "wheel",
        "--no-deps",
        "--disable-pip-version-check",
    ]
    if pre:
        args += ["--pre"]
    if cache_dir is not None:
        args += [
            "--wheel-dir",
            cache_dir,
        ]
    if index_url is not None:
        args += [
            "--index-url",
            index_url,
            "--trusted-host",
            urlparse(index_url).hostname,
        ]
    if extra_index_url is not None:
        args += [
            "--extra-index-url",
            extra_index_url,
            "--trusted-host",
            urlparse(extra_index_url).hostname,
        ]
    if PIP_VERSION >= [10]:
        args.append("--progress-bar=off")
    return args


def _get_available_versions(package, index_url, extra_index_url, pre):
    logger.debug("Finding possible versions for {}".format(package))
    args = _get_wheel_args(index_url, extra_index_url, pre) + [package + "==rubbish"]

    try:
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        # expected. we forced this by using a non-existing version number.
        out = getattr(err, "output", b"")
    else:
        logger.warning(out)
        raise RuntimeError("Unexpected success:" + " ".join(args))
    out = out.decode("utf-8").splitlines()
    for line in out[::-1]:
        if "Could not find a version that satisfies the requirement" in line:
            all_versions = line.split("from versions: ", 1)[1].rstrip(")").split(", ")
            if pre:
                return all_versions
            # filter out pre-releases
            logger.debug(
                str(
                    {
                        package: [
                            v for v in all_versions if not re.findall(r"[a-zA-Z]", v)
                        ]
                    }
                )
            )
            return [v for v in all_versions if not re.findall(r"[a-zA-Z]", v)]
    raise RuntimeError("Failed to get available versions for {}".format(package))


def _download_wheel(package, index_url, extra_index_url, pre, cache_dir):
    """Download/build wheel for package and return its filename."""
    logger.debug("Downloading/building wheel for {}".format(package))
    abs_cache_dir = os.path.abspath(os.path.expanduser(cache_dir))
    args = _get_wheel_args(index_url, extra_index_url, pre, cache_dir) + [package]
    try:
        out = subprocess.check_output(args, stderr=subprocess.STDOUT,)
    except subprocess.CalledProcessError as err:
        output = getattr(err, "output", b"").decode("utf-8")
        logger.error(output)
        raise
    out = out.decode("utf-8").splitlines()[::-1]
    for i, line in enumerate(out):
        if cache_dir in line or abs_cache_dir in line or "ephem-wheel-cache" in line:
            if line.strip().startswith("Stored in directory"):
                # wheel was built
                fname = [
                    part.replace("filename=", "")
                    for part in out[i + 1].split()
                    if part.startswith("filename=")
                ][0]
            else:
                # wheel was fetched
                fname = (
                    line.split(
                        abs_cache_dir if abs_cache_dir in line else cache_dir, 1
                    )[1].split(".whl", 1)[0]
                    + ".whl"
                )
            logger.debug(
                str({package: os.path.join(cache_dir, fname.lstrip(os.path.sep))})
            )
            return os.path.join(cache_dir, fname.lstrip(os.path.sep))
    raise RuntimeError("Failed to download wheel for {}".format(package))


def _extract_metadata(wheel_fname):
    wheel_fname = os.path.abspath(wheel_fname)
    logger.debug("Searching metadata in %s", wheel_fname)
    if not os.path.exists(wheel_fname):
        raise RuntimeError("File not found: {}".format(wheel_fname))
    info = get_metadata(wheel_fname)
    if info is None:
        raise RuntimeError("Failed to extract metadata: {}".format(wheel_fname))
    data = vars(info)
    data.pop("filename", None)
    return data


def _get_wheel_requirements(metadata, extras_requested):
    """Just the strings (name and spec) for my immediate dependencies. Cheap."""
    all_requires = metadata.get("requires_dist", [])
    if not all_requires:
        return []
    result = []
    env_data = default_environment()
    for req_str in all_requires:
        req = parse_req(req_str)
        req_short, _sep, _marker = str(req).partition(";")
        if req.marker is None:
            # unconditional dependency
            result.append(req_short)
            continue
        # conditional dependency - must be evaluated in environment context
        for extra in [None] + extras_requested:
            if req.marker.evaluate(dict(env_data, extra=extra)):
                logger.debug("included conditional dep %s", req_str)
                result.append(req_short)
                break
        else:
            logger.debug("dropped conditional dep %s", req_str)
    result = sorted(set(result))  # this makes the dep tree deterministic/repeatable
    return result


def discover_dependencies_and_versions(
    package, index_url, extra_index_url, cache_dir, pre
):
    """Get information for a package.

    Args:
        package (str): pip requirement format spec compliant package
        index_url (str): primary PyPI index url
        extra_index_url (str): secondary PyPI index url
        cache_dir (str): directory for storing wheels
        pre (bool): pip --pre flag

    Returns:
        dict: package information:
            'version': the version resolved by pip
            'available': all available versions resolved by pip
            'requires': all requirements as found in corresponding wheel (dist_requires)

    """
    req = parse_req(package)
    extras_requested = sorted(req.extras)

    wheel_fname = _download_wheel(
        req.__str__(), index_url, extra_index_url, pre, cache_dir
    )
    wheel_metadata = _extract_metadata(wheel_fname)
    wheel_requirements = _get_wheel_requirements(wheel_metadata, extras_requested)
    wheel_version = wheel_metadata["version"]
    available_versions = (
        _get_available_versions(req.key, index_url, extra_index_url, pre)
        if req.key != "."
        else [wheel_version]
    )
    if wheel_version not in available_versions:
        available_versions.append(wheel_version)

    return {
        "name": wheel_metadata["name"],
        "version": wheel_version,
        "available": available_versions,
        "requires": wheel_requirements,
    }

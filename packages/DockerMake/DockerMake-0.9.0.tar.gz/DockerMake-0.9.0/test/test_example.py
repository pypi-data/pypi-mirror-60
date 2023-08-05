import os
import uuid
import subprocess
import pytest

from .helpers import experimental_daemon

EXAMPLEDIR = os.path.join("../example")
THISDIR = os.path.dirname(__file__)


def test_executable_in_path():
    subprocess.check_call("which docker-make".split(), cwd=EXAMPLEDIR)


def test_help_string():
    subprocess.check_call("docker-make --help".split(), cwd=EXAMPLEDIR)


def test_list():
    subprocess.check_call("docker-make --list".split(), cwd=EXAMPLEDIR)

    output = subprocess.check_output("docker-make --list".split(), cwd=EXAMPLEDIR)

    expected = set(
        (
            "airline_data blank_file_build data_image data_science "
            "devbase final plant_data python_image base_image"
        ).split()
    )

    for line in list(output.splitlines())[4:]:
        image = line[3:].decode("utf-8")
        assert image in expected
        expected.remove(image)

    assert len(expected) == 0


def test_push_quay_already_logged_in():
    customtag = str(uuid.uuid1())
    if "QUAYUSER" in os.environ and "QUAYTOKEN" in os.environ:
        subprocess.check_call(
            [
                "docker",
                "login",
                "-u",
                os.environ["QUAYUSER"],
                "-p",
                os.environ["QUAYTOKEN"],
                "quay.io",
            ]
        )
    else:
        pytest.skip("Can't test quay push - no login info available")

    subprocess.check_call(
        [
            "docker-make",
            "testimage",
            "--repo",
            "quay.io/avirshup/docker-make-test-push-target:",
            "--tag",
            customtag,
            "--push",
        ],
        cwd=THISDIR,
    )

    subprocess.check_call(
        [
            "docker",
            "pull",
            "quay.io/avirshup/docker-make-test-push-target:testimage-%s" % customtag,
        ]
    )


def test_push_dockerhub_with_login():
    customtag = str(uuid.uuid1())
    if "DOCKERUSER" not in os.environ or "DOCKERTOKEN" not in os.environ:
        pytest.skip("Can't test dockerhub push - no login info available")

    user = os.environ["DOCKERUSER"]
    token = os.environ["DOCKERTOKEN"]

    subprocess.check_call(
        [
            "docker-make",
            "testimage",
            "--repo",
            "docker.io/%s/docker-make-test-push:" % user,
            "--tag",
            customtag,
            "--push",
            "--user",
            user,
            "--token",
            token,
        ],
        cwd=THISDIR,
    )

    subprocess.check_call(
        [
            "docker",
            "pull",
            "docker.io/avirshup/docker-make-test-push:testimage-%s" % customtag,
        ]
    )


def test_example_build(experimental_daemon):
    subprocess.check_call(
        "docker-make final --repo myrepo --tag mytag".split(), cwd=EXAMPLEDIR
    )

    subprocess.check_call(
        "docker run myrepo/final:mytag ls data/AirPassengers.csv data/inhibitor.csv data/file.txt".split(),
        cwd=EXAMPLEDIR,
    )


def test_get_console_width_no_stderr_on_failure():
    # run docker-make with a non-console standard input
    #   (inspiration from Python's subprocess.py)
    process = subprocess.Popen(
        "docker-make devbase --repo myrepo --tag mytag".split(),
        cwd=EXAMPLEDIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(b"I am not a shell")
    except:
        process.kill()
        process.wait()
        raise
    retcode = process.poll()
    assert retcode == 0  # sanity check - did this build not work for some reason?

    assert b"ioctl for device" not in stderr


TEMPNAME = "dmtest__python_test"


def test_write_then_build(tmpdir):
    tmppath = str(tmpdir)
    subprocess.check_call(
        "docker-make -n -p --dockerfile-dir %s blank_file_build" % tmppath,
        shell=True,
        cwd=EXAMPLEDIR,
    )
    subprocess.check_call(
        "docker rm %s; docker build . -f Dockerfile.blank_file_build -t %s"
        % (TEMPNAME, TEMPNAME),
        shell=True,
        cwd=tmppath,
    )

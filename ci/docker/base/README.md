# Base CI image

This Docker image is the shared lightweight CI environment for the early pipeline stages:

- VERSIONING
- STRUCTURE
- FORMAT
- LINT

## Purpose

This image provides a stable and reproducible toolchain for repository checks and static analysis without depending on whatever is installed on the Jenkins host or agent.

It is intentionally shared across the early CI stages.

## Included tools

- Python 3.12
- pip
- Black 25.11.0
- mypy
- pylint
- Node.js 22
- npm
- Prettier
- git
- bash

## Intended usage

This image should be used for stages that need only:

- shell scripts
- Python validation scripts
- repository structure checks
- formatter checks
- static linting and typing checks

It is not intended to contain the full dependency stack for heavier application tests or production builds.

Later pipeline stages may still use more specific images, for example:

- python-test image
- frontend-build image
- integration-test image

## Build the image locally

From the repository root:

```bash
docker build -t coldpool-ci-base:1 -f ci/docker/base/Dockerfile .
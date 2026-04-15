# Base CI image

This Docker image is the shared lightweight CI environment for the early pipeline stages:

- VERSIONING
- STRUCTURE
- FORMAT

## Purpose

This image provides a stable and reproducible toolchain for simple repository checks without depending on whatever is installed on the Jenkins host or agent.

It is intentionally small and generic.

## Included tools

- Python 3.12
- pip
- Black 25.11.0
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

It is not intended to contain the full dependency stack for application tests or production builds.

Later pipeline stages should usually use more specific images, for example:

- python-test image
- frontend-build image
- integration-test image

## Build the image locally

From the repository root:

```bash
docker build -t coldpool-ci-base:1 -f ci/docker/base/Dockerfile .
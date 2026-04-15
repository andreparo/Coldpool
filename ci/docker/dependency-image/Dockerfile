FROM coldpool-ci-base:1

WORKDIR /workspace

COPY apps/coldpool_web_app/package.json apps/coldpool_web_app/package-lock.json /workspace/apps/coldpool_web_app/
RUN cd /workspace/apps/coldpool_web_app && npm ci

# Optional backend dependency install.
# Enable this later only if backend smoke/unit/component tests need installed project dependencies.
# COPY apps/coldpool_server/pyproject.toml /workspace/apps/coldpool_server/
# RUN cd /workspace/apps/coldpool_server && python -m pip install --no-cache-dir -e .

WORKDIR /workspace
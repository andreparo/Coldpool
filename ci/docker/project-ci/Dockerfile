FROM coldpool-ci-base:1

WORKDIR /workspace

# Copy the whole repository snapshot from the Jenkins workspace build context
COPY . /workspace

# Frontend dependencies
RUN cd apps/coldpool_web_app && npm ci

# Optional backend dependency install.
# Keep this commented until you really need it.
# If coldpool_server has a proper pyproject and installable package, enable one of these:
# RUN python -m pip install --no-cache-dir -e apps/coldpool_server
# or:
# RUN cd apps/coldpool_server && python -m pip install --no-cache-dir -e .

# Default shell location
WORKDIR /workspace
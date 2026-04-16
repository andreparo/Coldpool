FROM coldpool-ci-base:1

WORKDIR /workspace

COPY apps/coldpool_web_app/package.json apps/coldpool_web_app/package-lock.json /workspace/apps/coldpool_web_app/
RUN cd /workspace/apps/coldpool_web_app && npm ci

RUN python3 -m pip install --no-cache-dir \
    pytest \
    playwright

RUN python3 -m playwright install --with-deps chromium

WORKDIR /workspace
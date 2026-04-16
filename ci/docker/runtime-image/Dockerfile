FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    sqlite3 \
    sudo \
    && rm -rf /var/lib/apt/lists/*

ARG PACKAGE_TARBALL_RELATIVE_PATH

WORKDIR /runtime-build

COPY ${PACKAGE_TARBALL_RELATIVE_PATH} /runtime-build/coldpool-package.tar.gz

RUN mkdir -p /runtime-build/extracted \
    && tar -xzf /runtime-build/coldpool-package.tar.gz -C /runtime-build/extracted

RUN package_dir="$(find /runtime-build/extracted -mindepth 1 -maxdepth 1 -type d | head -n 1)" \
    && test -n "$package_dir" \
    && COLDPOOL_NONINTERACTIVE=1 \
       COLDPOOL_INSTALL_ROOT=/opt/coldpool \
       COLDPOOL_DATA_ROOT=/var/lib/coldpool \
       COLDPOOL_CONFIG_ROOT=/etc/coldpool \
       COLDPOOL_LOG_ROOT=/var/log/coldpool \
       COLDPOOL_PORT=5000 \
       bash "$package_dir/install.sh"

EXPOSE 5000

WORKDIR /opt/coldpool

CMD ["/opt/coldpool/run.sh"]
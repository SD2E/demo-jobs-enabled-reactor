FROM sd2e/reactors:python3-edge
ARG DATACATALOG_BRANCH=2_0

# Comment out if not actively developing python-datacatalog
RUN pip uninstall --yes datacatalog

# Install from Repo
RUN NO_CACHE=$RANDOM pip3 install --upgrade \
    --no-cache-dir "git+https://github.com/SD2E/python-datacatalog.git@${DATACATALOG_BRANCH}"

ENV CATALOG_ADMIN_TOKEN_KEY=ErWcK75St2CUetMn7pzh8EwzAhn9sHHK54nA
ENV CATALOG_RECORDS_SOURCE=demo-jobs-reactor-app
ENV CATALOG_STORAGE_SYSTEM=data-sd2e-community

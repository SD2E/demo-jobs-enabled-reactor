FROM sd2e/reactors:python3-edge
ARG DATACATALOG_BRANCH=2_0

# Comment out if not actively developing python-datacatalog
RUN pip uninstall --yes datacatalog

# Install from Repo
RUN pip3 install --upgrade \
    --no-cache-dir "git+https://github.com/SD2E/python-datacatalog.git@${DATACATALOG_BRANCH}"

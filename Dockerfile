FROM sd2e/reactors:python3-edge

ARG DATACATALOG_BRANCH=0_2_0

FROM sd2e/reactors:python3-edge

# reactor.py, config.yml, and message.jsonschema will be automatically
# added to the container when you run docker build or abaco deploy
# ADD tests/data /data

# Comment out if not actively developing python-datacatalog
RUN pip uninstall --yes datacatalog

# Install from Repo
RUN pip3 install --upgrade \
    --no-cache-dir "git+https://github.com/SD2E/python-datacatalog.git@${DATACATALOG_BRANCH}"

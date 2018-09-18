FROM sd2e/reactors:python3-edge

# reactor.py, config.yml, and message.jsonschema will be automatically
# added to the container when you run docker build or abaco deploy
COPY datacatalog /datacatalog

# RUN apt-get update && \
#     apt-get -y install python-pydot python-pydot-ng graphviz libgraphviz-dev

# RUN pip3 install pydot pygraphviz transitions[diagrams]

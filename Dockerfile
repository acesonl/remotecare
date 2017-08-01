from ossobv/uwsgi-python

ADD requirements.txt /requirements.txt

RUN set -ex \
	&& buildDeps=' \
		gcc \
		sloccount \ 
		libffi-dev \ 
		libgraphviz-dev \ 
		graphviz \ 
		graphviz-dev \ 
		python-dev \ 
		pkg-config \
		libjpeg-dev \
	' \
	&& apt-get update && apt-get install -y $buildDeps --no-install-recommends \
	&& apt-get install -y python-imaging libxml2-dev libxslt1-dev language-pack-nl libmysqlclient-dev npm --no-install-recommends \
	&& npm -g install yuglify \
	&& ln -s /usr/bin/nodejs /usr/bin/node \ 
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
	&& rm -rf /usr/src/python ~/.cache

ADD remotecare /remotecare
WORKDIR /remotecare
RUN python manage.py collectstatic --noinput

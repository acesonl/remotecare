Install Remote Care
===================

The steps below show the procedure for getting Remote Care
running on a single machine. But with some knowledge of mysql
and nginx/apache you should be able to get it running in an environment
with separate database and webservers as well.

    ..  note::

        The install process has been successfully tested on Ubuntu 14.04 lts (x64).
        But should also work on newer Ubuntu versions and other Debian based Linux
        distributions. Others (RPM based, other) are also a possibilty but you need
        to figure out which packages correspond to the DPKG ones and probably
        need to search Google a lot for fixes concerning the differences between 
        the two.

:subtitle:`Step 1: Clone repository`
Setup directory structure and clone repository::

    #Create directory, default to /srv/remotecare
    sudo mkdir /srv/remotecare/
    sudo chown $USER:$USER /srv/remotecare/
    mkdir /srv/remotecare/default
    cd /srv/remotecare/default

    #install git
    sudo apt-get install git

    #replace #username# with your username for the repository
    git clone #username#@10.101.139.250:/srv/git/remotecare.git ./

:subtitle:`Step 2: Install prerequisites and dependencies`
Install all needed packages::

    #Install virtualenv, nginx and uwsgi
    #Remove nginx and uwsgi if you only are going to use
    #the internal manage.py runserver
    sudo apt-get install python-dev python-virtualenv
    sudo apt-get install nginx
    sudo apt-get install uwsgi uwsgi-plugin-python

    #Install package dependencies for Remote Care
    #Does also install yuglify for css/js compression
    /srv/remotecare/default/package_dependencies.sh

:subtitle:`Step 3: Setup virtualenv`
Setup virtualenv and install pip packages::

    #create virtualenv
    virtualenv /srv/remotecare/virtpy

    #activate the virtual env and install requirements
    source /srv/remotecare/virtpy/bin/activate
    pip install -r /srv/remotecare/default/requirements.txt

:subtitle:`Step 4: Setup database`
Very basic setup for getting a database running in mysql::

    #Setup database (mysql)
    mysql -u root -p

    #Use different users & passwords and check collation.
    CREATE DATABASE remote_care_db;
    CREATE USER remote_care@localhost IDENTIFIED BY 'remote_care';
    GRANT ALL PRIVILEGES ON remote_care_db.* to remote_care;
    FLUSH PRIVILEGES;

    #Return to the default user
    exit

    vim /srv/remotecare/default/remotecare/remotecare/server_settings.py
    #Include the settings for the server::
    --------------------------------------------------
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG

    DATABASES = {
        'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'remote_care_db',
        'USER': 'remote_care',                      # Not used with sqlite3.
        'PASSWORD': 'remote_care',                  # Not used with sqlite3.
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
        },
    }
    --------------------------------------------------

:subtitle:`Step 5: Sync Django models with database and collect static`
Sync de Django models to the database and/or setup tables::

    #Note, you need to have the virtualenv activated
    cd /srv/remotecare/default/remotecare

    #Create datatables
    python manage.py migrate

    #Insert initial data (hospitals etc.)
    python manage.py loaddata apps/lists/fixtures/initial_data.json
    python manage.py loaddata apps/questionnaire/qol/fixtures/initial_data.json
    python manage.py loaddata apps/questionnaire/ibd/fixtures/initial_data.json

    #Also collect static files
    python manage.py collectstatic --noinput

    # insert the demo test data
    # Manager user auto added email:manager@example.com, pssw:remotecare
    python insert_test_data.py

    # Django test/development server: python manage.py runserver 0:8000

:subtitle:`Step 6: Setup uwsgi init script`
Setup an init script for uwsgi::

    #Copy simple default uwsgi config & start uwsgi
    sudo cp /srv/remotecare/default/remotecare/remotecare/uwsgi.ini /etc/uwsgi/apps-available/remotecare.ini
    sudo ln -s /etc/uwsgi/apps-available/remotecare.ini /etc/uwsgi/apps-enabled/remotecare.ini
    sudo service uwsgi restart

    #See if uswgi runs: Check "ps fax" and "netstat -a"
    #Error checking: tail -f /var/log/uwsgi/apps/remotecare.log

:subtitle:`Step 7: Setup nginx`
Setup nginx with uswgi::

    #Copy simple default nginx config & start nginx
    sudo cp /srv/remotecare/default/remotecare/remotecare/nginx /etc/nginx/sites-available/default 
    sudo service nginx restart
    
    #See if nginx runs: Check "ps fax"
    #Error checking: tail -f /var/log/nginx/error.log
	
:subtitle:`Step 8: Check if website runs`
The website should now be running at the default IP of the server!


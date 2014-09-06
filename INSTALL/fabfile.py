import os

from fabric.api import *
from fabric.contrib.files import append
from fabric.colors import green


def cmd(*args, **kwargs):
    """ use sudo if current user is not root """
    if env['user'] == 'root':
        return run(*args, **kwargs)
    else:
        return sudo(*args, **kwargs)


def install():
    initialize()
    initialize_server()
    initialize_db()
    initialize_ssl()
    install_dependencies()
    create_db()
    create_python_virtualenv()
    install_python_requirements()
    create_project()
    edit_settings()
    install_redis()
    sync_data()
    create_admin()
    configure_nginx()
    install_uwsgi()
    configure_supervisor()
    install_postfix()
    restart_services()
    completed_message()


def update(**kwargs):
    global root_dir
    global fabfile_dir
    global project_dir
    global project_name
    root_dir = kwargs.get('root_dir', '/var/www/')  # defaults to /var/www/
    project_name = kwargs.get('project_name')
    # if no parameter supplied
    if project_name is None:
        # ask
        initialize_dirs()
    install_python_requirements()
    sync_data(update=True)
    restart_services()


# ------ internal functions ------ #


def initialize():
    if 'root_dir' not in globals():
        initialize_dirs()


def initialize_dirs():
    global root_dir
    global project_name
    global project_dir
    global fabfile_dir
    global tmp_dir
    root_dir = prompt('Set install directory (including trailing slash): ', default='/var/www/')
    project_name = prompt('Set project name: ', default='myproject')
    project_dir = '%s%s' % (root_dir, project_name)
    fabfile_dir = os.path.dirname(__file__)
    tmp_dir = '~/nodeshot_install'


def initialize_server():
    if 'server_name' not in globals():
        global server_name
        server_name = prompt('Server name: ', default=env['host'])


def initialize_db():
    db_params = ('db_user','db_pass')
    for db_param in db_params:
        if db_param not in globals():
            global db_user
            global db_pass
            db_user = prompt('Set database user: ', default='nodeshot')
            db_pass = prompt('Set database user password: ')


def initialize_ssl():
    print(green("****************************************"))
    print(green("Please insert SSL certificate details..."))
    print(green("****************************************"))

    run('mkdir -p %s' % tmp_dir)
    with cd(tmp_dir):
        run('openssl req -new -x509 -nodes -days 365 -out server.crt -keyout server.key')


def install_dependencies():
    initialize()
    print(green("Installing required packages. This may take a while..."))
    with hide('stdout', 'stderr'):
        cmd('apt-get update -y')
        path = '{path}/dependencies.txt'.format(path=fabfile_dir)
        # read dependencies, put them on one line
        dependencies = ' '.join([line.replace('\n', '') for line in open(path).readlines()])
        # install
        cmd('apt-get install -y %s' % dependencies)
        # install GEOS
        with settings(warn_only=True):
            geos_installed = bool(run('dpkg --get-selections | grep "geos\s"'))
        if not geos_installed:
            with cd(tmp_dir):
                cmd('wget http://download.osgeo.org/geos/geos-3.3.8.tar.bz2')
                cmd('tar xvfj geos-3.3.8.tar.bz2')
            with cd('%s/geos-3.3.8' % tmp_dir):
                cmd('./configure')
                cmd('make')
                cmd('checkinstall -y')
        # install Postgis 2
        with settings(warn_only=True):
            postgis_installed = bool(run('dpkg --get-selections | grep "postgis\s"'))
        if not postgis_installed:
            with cd(tmp_dir):
                cmd('wget http://download.osgeo.org/postgis/source/postgis-2.0.3.tar.gz')
                cmd('tar xfvz postgis-2.0.3.tar.gz')
            with cd('%s/postgis-2.0.3' % tmp_dir):
                cmd('./configure')
                cmd('make')
                cmd('checkinstall -y')


def create_db():
    initialize_db()
    print(green("Configuring DB..."))
    with hide('stdout', 'stderr'):
        cmd('su - postgres -c "createdb nodeshot"')
        cmd('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION hstore;\'"')
        cmd('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis;\'"')
        cmd('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis_topology;\'"')
        cmd('su - postgres -c "createuser %s  -R -S -D"'  % db_user)
        cmd('sudo -u postgres psql -U postgres -c "ALTER USER %s WITH PASSWORD \'%s\';"' % (db_user, db_pass))
        cmd('su - postgres -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE nodeshot to %s;\'"' % db_user)
        cmd('su - postgres -c "psql nodeshot -c \'GRANT ALL PRIVILEGES ON TABLE spatial_ref_sys TO %s;\'"' % db_user)


def create_python_virtualenv():
    initialize()
    print(green("Creating virtual env..."))
    with hide('stdout', 'stderr'):
        cmd('pip install virtualenvwrapper')
        cmd("echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bash_profile")
        cmd("echo 'source /usr/local/bin/virtualenvwrapper.sh' >> /root/.bashrc")
        cmd("chown -R {user}:{user} ~/.virtualenvs".format(user=env['user']))
        run('mkvirtualenv nodeshot')


def install_python_requirements():
    initialize()
    print(green("Installing requirements. This may take a while..."))
    with hide('stdout', 'stderr'):
        run('workon nodeshot && pip install -U distribute')
        run('workon nodeshot && pip install -U https://github.com/ninuxorg/nodeshot/tarball/master')


def create_project():
    initialize()
    print(green("Creating project..."))
    
    cmd('mkdir -p /var/www/')
    with cd('/var/www/'):
        cmd('workon nodeshot && nodeshot startproject %s' % project_name)
    with cd('/var/www/%s' % project_name):
        cmd('chown -R %s:www-data .' % env['user'])
        cmd('adduser www-data %s' % env['user'])
        cmd('chmod 775 . log %s' % project_name)
        cmd('chmod 750 manage.py ./%s/*.py' % project_name)


def edit_settings():
    initialize()
    initialize_db()
    initialize_server()
    print(green("Creating Nodeshot config..."))

    with cd ('%s/%s' % (project_dir, project_name)):
        cmd('sed -i \'s#<user>#%s#g\' settings.py' % db_user)
        cmd('sed -i \'s#<password>#%s#g\' settings.py' % db_pass)
        cmd('sed -i \'s#<domain>#%s#g\' settings.py' % server_name)
        cmd('sed -i \'s#DEBUG = True#DEBUG = False#g\' settings.py')


def install_redis():
    initialize()
    print(green("Installing redis..."))
    with hide('stdout', 'stderr'):
        cmd('add-apt-repository -y ppa:chris-lea/redis-server')
        cmd('apt-get -y update')
        cmd('apt-get -y --force-yes install redis-server')
        run('workon nodeshot && pip install -U celery[redis]')
        cmd('echo 1 > /proc/sys/vm/overcommit_memory')
        cmd('service redis-server restart')


def sync_data(update=None):
    initialize()
    print(green("Initializing Nodeshot..."))
    sync_command = './manage.py syncdb --noinput && ./manage.py migrate && ./manage.py collectstatic --noinput'
    if update is not None:
        sync_command = './manage.py syncdb --no-initial-data && ./manage.py migrate --no-initial-data && ./manage.py collectstatic --noinput'
    with cd (project_dir):
        run('workon nodeshot && %s' % sync_command)


def create_admin():
    initialize()
    print(green("Creating Nodeshot admin account..."))
    create_admin_oneliner = """echo "from nodeshot.community.profiles.models import Profile;\
                            Profile.objects.create_superuser('admin', '', 'admin')" | ./manage.py shell"""
    with cd(project_dir):
        cmd('workon nodeshot && %s' % create_admin_oneliner)


def configure_nginx():
    initialize()
    initialize_server()
    print(green("Configuring Nginx..."))
    nginx_dir = '/etc/nginx/ssl'
    cmd('mkdir -p %s' % nginx_dir)
    with cd (nginx_dir):
        print(green("Insert Certificate details..."))
        cmd('cp ~/nodeshot_install/server.crt .')
        cmd('cp ~/nodeshot_install/server.key .')

    cmd('cp /etc/nginx/uwsgi_params /etc/nginx/sites-available/')
    
    nginx_conf = open('%s/nginx.conf' % fabfile_dir).read()
    append(filename='/etc/nginx/sites-available/%s' % server_name,
           text=nginx_conf,
           use_sudo=True)

    with cd('/etc/nginx/sites-available'):
        cmd('sed -i \'s#nodeshot.yourdomain.com#%s#g\' %s' % (server_name, server_name))
        cmd('sed -i \'s#PROJECT_PATH#%s#g\' %s' % (project_dir, server_name))
        cmd('sed -i \'s#PROJECT_NAME#%s#g\' %s' % (project_name, server_name))
        cmd('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (server_name, server_name))
    
    cmd('service nginx configtest')


def install_uwsgi():
    initialize()
    with hide('stdout', 'stderr'):
        cmd('pip install uwsgi')
    
    uwsgi_ini = open('%s/uwsgi.ini' % fabfile_dir).read()
    append(filename='%s/uwsgi.ini' % project_dir,
           text=uwsgi_ini,
           use_sudo=True)
    
    with cd (project_dir):
        python_home = '%s/nodeshot' % run('echo $WORKON_HOME')
        cmd('sed -i \'s#PROJECT_PATH#%s#g\' uwsgi.ini' % project_dir)
        cmd('sed -i \'s#PROJECT_NAME#%s#g\' uwsgi.ini' % project_name)
        cmd('sed -i \'s#PYTHON_HOME#%s#g\' uwsgi.ini' % python_home)


def configure_supervisor():
    initialize()
    print(green("Installing & configuring Supervisor..."))
    with hide('stdout', 'stderr'):
        uwsgi_conf = open('%s/uwsgi.conf' % fabfile_dir).read()
        append(filename='/etc/supervisor/conf.d/uwsgi.conf', text=uwsgi_conf, use_sudo=True)
        
        celery_conf = open('%s/celery.conf' % fabfile_dir).read()
        append(filename='/etc/supervisor/conf.d/celery.conf', text=celery_conf, use_sudo=True)
        
        celerybeat_conf = open('%s/celery-beat.conf' % fabfile_dir).read()
        append(filename='/etc/supervisor/conf.d/celery-beat.conf', text=celerybeat_conf, use_sudo=True)
        
        with cd ('/etc/supervisor/conf.d/'):
            python_home = '%s/nodeshot' % run('echo $WORKON_HOME')
            cmd('sed -i \'s#PROJECT_PATH#%s#g\' uwsgi.conf' % project_dir)
            cmd('sed -i \'s#PROJECT_PATH#%s#g\' celery.conf' % project_dir)
            cmd('sed -i \'s#PROJECT_NAME#%s#g\' celery.conf' % project_name)
            cmd('sed -i \'s#PYTHON_HOME#%s#g\' celery.conf' % python_home)
            cmd('sed -i \'s#PROJECT_PATH#%s#g\' celery-beat.conf' % project_dir)
            cmd('sed -i \'s#PROJECT_NAME#%s#g\' celery-beat.conf' % project_name)
            cmd('sed -i \'s#PYTHON_HOME#%s#g\' celery-beat.conf' % python_home)
        
        cmd('supervisorctl update')


def install_postfix():
    initialize()
    initialize_server()
    with hide('stdout', 'stderr'):
        cmd('export DEBIAN_FRONTEND=noninteractive && apt-get -y install postfix')
        postfix_conf = open('%s/postfix.cf' % fabfile_dir).read()
        append(filename='/etc/postfix/main.cf', text=postfix_conf, use_sudo=True)
        cmd('sed -i \'s#nodeshot.yourdomain.com#%s#g\' /etc/postfix/main.cf' % server_name)


def restart_services():
    initialize()
    print(green("Starting Nodeshot server..."))
    with cd (project_dir):
        cmd('service nginx restart && supervisorctl restart all')
    print(green("Nodeshot server started"))
    print(green("Cleaning installation directory..."))
    cmd('rm -rf ~/nodeshot_install')
    print(green("Installation completed"))


def completed_message():
    initialize_server()
    print(green("Cleaning installation directory..."))
    cmd('rm -rf ~/nodeshot_install')
    print(green("\nINSTALLATION COMPLETED !\n"))
    print(green("#############################################################"))
    print(green("                           WARNING:                         "))
    print(green(" Superuser is currently set as 'admin' with password 'admin'"))
    print(green(" Log in on https://%s/admin and change it " % server_name))
    print(green("#############################################################"))

from fabric.api import *
from fabric.contrib.files import append
from fabric.colors import green
import random
import json
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
secret_key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))



# Put host(s) configuration here or use -h switch on command line
# env.hosts = ''
# env.password = ''

git_repo = 'https://github.com/ninuxorg/nodeshot.git'


def initialize():
    install_dirs = ('root_dir','deploy_dir','project_dir')
    for install_dir in install_dirs:
        if install_dir not in globals():
            initialize_dirs()

def initialize_server():
    if 'server_name' not in globals():
        global server_name
        server_name = prompt('Server name: ')
       
def initialize_db():
    db_params = ('db_user','db_pass')
    for db_param in db_params:
        if db_param not in globals():
            global db_user
            global db_pass
            db_user = prompt('Set database user: ', default='nodeshot')
            db_pass = prompt('Set database user password: ', )
            
def initialize_dirs():        
    global root_dir
    global deploy_dir
    global project_dir
    root_dir = prompt('Set install directory ( including trailing slash ): ', default='/var/www/')
    project_name = prompt('Set project name: ', default='myproject')
    deploy_dir = '%snodeshot/' % root_dir
    project_dir = '%sprojects/ninux' % deploy_dir

def uninstall():
    initialize()
    with cd(project_dir):
        run('cat dependencies.txt | xargs apt-get -y purge')
    
def install():
    initialize()
    initialize_server()
    initialize_db()
    install_git()
    clone()
    install_dependencies()
    create_virtual_env()
    install_requirements()
    create_db()
    nginx_config()
    supervisor_config()
    redis_install()
    create_settings()
    sync_data() # Fails if settings are not correctly set
    start_server()

def update():
    initialize()
    pull()
    install_requirements()
    sync_data()  
      
def clone():
    initialize()
    print(green("Cloning repository..."))
    with hide('stdout', 'stderr'):
        run('mkdir -p  %s' % root_dir)
        with cd (root_dir):
            run('git clone %s nodeshot' % git_repo  )
        with cd (deploy_dir):
            run ('git checkout deploy_test') # to be removed when merged into master

def install_git():
    print(green("Installing Git..."))
    with hide('stdout', 'stderr'):
        run('apt-get -y install git-core')
        
def install_dependencies():
    initialize()
    print(green("Installing required packages. This may take a while..."))
    with hide( 'stdout', 'stderr'):
        with cd('%sinstall' % deploy_dir):
            run('cat dependencies.txt | xargs apt-get -y install')
        with cd('/tmp'):
            run('cp %s/install* . && ./install_GEOS.sh && ./install_Postgis.sh' % project_dir )

def pull():
    initialize()
    with cd (deploy_dir):
        run('pwd')
        run('git pull')

def create_virtual_env():
    print(green("Creating virtual env..."))
    with hide( 'stdout', 'stderr'):
        with cd (project_dir):
            run('virtualenv python')

def install_requirements():
    initialize()
    print(green("Installing requirements. This may take a while..."))
    with hide( 'stdout', 'stderr'):
        virtual_env = 'source python/bin/activate'
        pip_command = 'python/bin/pip install -r %srequirements.txt' % deploy_dir
        distribute_command = 'python/bin/pip install -U distribute'
        with cd (project_dir):
            run( virtual_env + ' &&  ' + pip_command  + ' &&  ' + distribute_command)
 
def create_db():
    initialize_db()
    print(green("Configuring DB..."))
    with hide( 'stdout', 'stderr'):
        run ('su - postgres -c "createdb nodeshot"')
        run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION hstore;\'"')
        run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis;\'"')
        run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis_topology;\'"')
        run ('su - postgres -c "createuser %s  -R -S -D "'  % db_user)
        run ('sudo -u postgres psql -U postgres -d postgres -c \"alter user %s with password \'%s\';\"' % (db_user,db_pass))
        run ('su - postgres -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE "nodeshot" to %s \'"' % db_user)
        
def sync_data():
    initialize()
    print(green("Initializing Nodeshot..."))
    virtual_env = 'source python/bin/activate'
    sync_command = 'python manage.py syncdb && python manage.py migrate && python manage.py collectstatic'
    with cd (project_dir):
        run( virtual_env + ' &&  ' + sync_command)
    
def nginx_config():
    initialize()
    print(green("Configuring Nginx..."))
    nginx_dir = '/etc/nginx/ssl'
    run ('mkdir -p %s' % nginx_dir)
    with cd (nginx_dir):
        print(green("Insert Certificate details..."))
        run ('openssl req -new -x509 -nodes -out server.crt -keyout server.key')
    run('cp /etc/nginx/uwsgi_params /etc/nginx/sites-available/')
    #run ('mkdir -p /var/www/nodeshot/public_html')
    
    run ('cp %s/nodeshot.yourdomain.com /etc/nginx/sites-available/nodeshot.yourdomain.com' % project_dir)

    with cd('/etc/nginx/sites-available'):
        run ('sed \'s/nodeshot.yourdomain.com/%s/g\' nodeshot.yourdomain.com > %s' % (server_name,server_name))
        run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' %s ' % (project_dir,server_name))
        run ('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (server_name,server_name))
    
def supervisor_config():
    initialize()
    print(green("Configuring Supervisor..."))
    with hide( 'stdout', 'stderr'):
        run ('pip install uwsgi')
        with cd (project_dir):
            run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' uwsgi.ini ' % project_dir)
        run ('cp %s/uwsgi.conf /etc/supervisor/conf.d/uwsgi.conf' % project_dir)
        run ('cp %s/celery.conf /etc/supervisor/conf.d/celery.conf' % project_dir)
        run ('cp %s/celery-beat.conf /etc/supervisor/conf.d/celery-beat.conf' % project_dir)
        with cd ('/etc/supervisor/conf.d/'):
            run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' uwsgi.conf ' % project_dir)
            run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' celery.conf ' % project_dir)
            run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' celery-beat.conf ' % project_dir)
        run('supervisorctl update')
    
def redis_install():
    initialize()
    print(green("Installing redis..."))
    with hide( 'stdout', 'stderr'):
        virtual_env = 'source python/bin/activate'
        pip_command = 'python/bin/pip install -U celery[redis]'
        run('add-apt-repository -y ppa:chris-lea/redis-server')
        run('apt-get -y update')
        run('apt-get -y install redis-server')
        with cd (project_dir):
            run( virtual_env + ' &&  ' + pip_command)

def create_settings():
    initialize()
    initialize_db()
    initialize_server()
    print(green("Creating Nodeshot config..."))
    local_settings = "DEBUG = False \n" 
    local_settings += "APP_PATH = '%s' \n" % deploy_dir
    local_settings += "SECRET_KEY = '%s' \n" % secret_key
    local_settings += "DOMAIN = '%s' \n" % server_name
    local_settings += "ALLOWED_HOSTS = ['*']\n"
        
    DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nodeshot',                      # Or path to database file if using sqlite3.
        'USER': db_user,                      # Not used with sqlite3.
        'PASSWORD': db_pass,                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

    db_settings = json.dumps(DATABASES)
    with hide( 'stdout', 'stderr'):
        with cd ('%s/ninux' % project_dir):
            append('local_settings.py', local_settings)
            append('local_settings.py', 'DATABASES = %s' % db_settings)
            run('cp production_settings.example.py settings.py')
        
        
def start_server():
    initialize()
    print(green("Starting Nodeshot server..."))
    with cd (project_dir):
        run('touch log/ninux.error.log')
        run('chmod 666 log/ninux.error.log')
        run('service nginx restart && supervisorctl restart all')
    print(green("Nodeshot server started"))   

    


    

import json

from fabric.api import *
from fabric.contrib.files import append
from fabric.colors import green

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
        
def initialize_ssl():
    print(green("****************************************"))
    print(green("Please insert SSL certificate details..."))
    print(green("****************************************"))
    run ('mkdir -p /tmp/nodeshot_install')
    with cd('/tmp/nodeshot_install'):
        run ('openssl req -new -x509 -nodes -days 365 -out server.crt -keyout server.key')
       
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
    global project_name
    root_dir = prompt('Set install directory ( including trailing slash ): ', default='/var/www/')
    project_name = prompt('Set project name: ', default='myproject')
    deploy_dir = '%snodeshot/' % root_dir
    project_dir = '%sprojects/%s' % (deploy_dir,project_name)

def uninstall():
    initialize()
    with cd(project_dir):
        run('cat dependencies.txt | xargs apt-get -y purge')
    
def install():
    initialize()
    initialize_server()
    initialize_db()
    initialize_ssl()
    install_git()
    clone()
    install_dependencies()
    install_postfix()
    create_virtual_env()
    install_requirements()
    create_project()
    create_db()
    create_settings()
    sync_data() # Fails if settings are not correctly set
    create_admin()
    nginx_config()
    supervisor_config()
    redis_install()
    start_server()
    warning_message()

def update():
    initialize()
    pull()
    install_requirements()
    sync_data()  
    start_server()
    
def clone():
    initialize()
    print(green("Cloning repository..."))
    with hide('stdout', 'stderr'):
        run('mkdir -p  %s' % root_dir)
        with cd (root_dir):
            run('git clone %s nodeshot' % git_repo  )
        #with cd (deploy_dir):
        #    run ('git checkout deploy_test') # to be removed when merged into master

def install_git():
    print(green("Installing Git..."))
    with hide('stdout', 'stderr'):
        run('apt-get -y install git-core')
        
def install_dependencies():
    initialize()
    print(green("Installing required packages. This may take a while..."))
    run('apt-get update')
    with hide( 'stdout', 'stderr'):
        with cd('%sINSTALL' % deploy_dir):
            run('cat dependencies.txt | xargs apt-get -y install')
        with cd('/tmp/nodeshot_install'):
            run('cp %sINSTALL/install* . && ./install_GEOS.sh && ./install_Postgis.sh' % deploy_dir )

def install_postfix():
    initialize()
    initialize_server()
    with hide( 'stdout', 'stderr'):
        with cd('%sINSTALL' % deploy_dir):
            run('export DEBIAN_FRONTEND=noninteractive && apt-get -y install postfix')
            run ('cp main.cf /etc/postfix/main.cf')
            run ('sed -i \'s#nodeshot.yourdomain.com#%s#g\' /etc/postfix/main.cf ' % server_name)

def pull():
    initialize()
    with cd (deploy_dir):
        run('pwd')
        run('git pull')

def create_virtual_env():
    initialize()
    print(green("Creating virtual env..."))
    with hide( 'stdout', 'stderr'):
        run ('mkdir -p %s' % project_dir)
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

def create_project():
    initialize()
    print(green("Creating project..."))
    virtual_env = 'source python/bin/activate'
    template_name = "%sINSTALL/project_template" % deploy_dir
    create_project_command = "django-admin.py startproject %s --template=%s ." % (project_name,template_name)
    with hide( 'stdout', 'stderr'):
        with cd (project_dir):
            run( virtual_env + ' &&  ' + create_project_command  )
 
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

def create_settings():
    initialize()
    initialize_db()
    initialize_server()
    print(green("Creating Nodeshot config..."))
    settings= {}
    settings['app_path'] = "APP_PATH = '%s' " % deploy_dir
    settings['domain'] = "DOMAIN = '%s' " % server_name
    
    DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', 
        'NAME': 'nodeshot',                      
        'USER': db_user,                      
        'PASSWORD': db_pass,                 
        'HOST': '127.0.0.1',                      
        'PORT': '',  
        }
    }

    db_settings = json.dumps(DATABASES)
    with cd ('%s/%s' % (project_dir,project_name)):
        run('rm -f local_settings.py')
        for setting,value in settings.iteritems():             
            append('local_settings.py', value)
        append('local_settings.py', 'DATABASES = %s' % db_settings)
        
def sync_data():
    initialize()
    print(green("Initializing Nodeshot..."))
    virtual_env = 'source python/bin/activate'
    sync_command = 'python manage.py syncdb --noinput && python manage.py migrate && python manage.py collectstatic --noinput'
    with cd (project_dir):
        run('mkdir -p log'  )
        run('touch log/%s.error.log' % project_name )
        run('chmod 666 log/%s.error.log' % project_name)
        run( virtual_env + ' &&  ' + sync_command)

def create_admin():
    initialize()
    print(green("Creating Nodeshot admin account..."))
    virtual_env = 'source python/bin/activate'
    create_admin_command = 'python manage.py loaddata %sINSTALL/admin_fixture.json' % deploy_dir
    with cd (project_dir):
        run( virtual_env + ' &&  ' + create_admin_command)
        
def nginx_config():
    initialize()
    initialize_server()
    print(green("Configuring Nginx..."))
    nginx_dir = '/etc/nginx/ssl'
    run ('mkdir -p %s' % nginx_dir)
    with cd (nginx_dir):
        print(green("Insert Certificate details..."))
        run ('cp /tmp/nodeshot_install/server.crt .')
        run ('cp /tmp/nodeshot_install/server.key .')

    run('cp /etc/nginx/uwsgi_params /etc/nginx/sites-available/')
    #run ('mkdir -p /var/www/nodeshot/public_html')
    
    run ('cp %sINSTALL/nodeshot.yourdomain.com /etc/nginx/sites-available/nodeshot.yourdomain.com' % deploy_dir)

    with cd('/etc/nginx/sites-available'):
        run ('sed \'s/nodeshot.yourdomain.com/%s/g\' nodeshot.yourdomain.com > %s' % (server_name,server_name))
        run ('sed -i \'s#PROJECT_PATH#%s#g\' %s ' % (project_dir,server_name))
        run ('sed -i \'s#PROJECT_NAME#%s#g\' %s ' % (project_name,server_name))
        run ('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (server_name,server_name))
    
def supervisor_config():
    initialize()
    print(green("Configuring Supervisor..."))
    with hide( 'stdout', 'stderr'):
        run ('pip install uwsgi')
        with cd (project_dir):
            run ('cp %sINSTALL/uwsgi.ini .' % deploy_dir)
            run ('sed -i \'s#PROJECT_PATH#%s#g\' uwsgi.ini ' % project_dir)
            run ('sed -i \'s#PROJECT_NAME#%s#g\' uwsgi.ini ' % project_name)
        run ('cp %sINSTALL/uwsgi.conf /etc/supervisor/conf.d/uwsgi.conf' % deploy_dir)
        run ('cp %sINSTALL/celery.conf /etc/supervisor/conf.d/celery.conf' % deploy_dir)
        run ('cp %sINSTALL/celery-beat.conf /etc/supervisor/conf.d/celery-beat.conf' % deploy_dir)
        with cd ('/etc/supervisor/conf.d/'):
            run ('sed -i \'s#PROJECT_PATH#%s#g\' uwsgi.conf ' % project_dir)
            run ('sed -i \'s#PROJECT_PATH#%s#g\' celery.conf ' % project_dir)
            run ('sed -i \'s#PROJECT_NAME#%s#g\' celery.conf ' % project_name)
            run ('sed -i \'s#PROJECT_PATH#%s#g\' celery-beat.conf ' % project_dir)
            run ('sed -i \'s#PROJECT_NAME#%s#g\' celery-beat.conf ' % project_name)
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
        
def start_server():
    initialize()
    print(green("Starting Nodeshot server..."))
    with cd (project_dir):
        run('service nginx restart && supervisorctl restart all')
    print(green("Nodeshot server started"))
    print(green("Cleaning installation directory..."))
    run ('rm -rf /tmp/nodeshot_install')
    print(green("Installation completed"))
    
def warning_message():
    initialize_server()
    print(green("Cleaning installation directory..."))
    run ('rm -rf /tmp/nodeshot_install')
    print(green("\nINSTALLATION COMPLETED !\n"))
    print (green("############################################################"))
    print (green("                      WARNING:                     "))
    print (green(" Superuser is currently set as 'admin' with password 'admin'"))
    print (green(" Logon on %s/admin and change it " % server_name))
    print (green("############################################################"))    
    


    

from fabric.api import *

# Put host(s) configuration here or use -h switch on command line
# env.hosts = ''
# env.password = ''


git_repo = 'https://github.com/ninuxorg/nodeshot.git'

#global root_dir
#global deploy_dir
#global project_dir

def initialize():
    install_dirs = ('root_dir','deploy_dir','project_dir')
    for install_dir in install_dirs:
        if install_dir not in globals():
            initialize_dirs()
            
def initialize_dirs():        
    global root_dir
    global deploy_dir
    global project_dir
    root_dir = prompt('Set install directory ( including trailing slash ): ', default='/var/www/')
    deploy_dir = '%snodeshot/' % root_dir
    project_dir = '%sprojects/ninux' % deploy_dir

def uninstall():
    initialize()
    with lcd(project_dir):
        local('cat dependencies.txt | xargs apt-get -y purge')
    
def install():
    initialize()
    clone()
    #install_dependencies()
    #create_virtual_env()
    #install_requirements()
    #create_db()
    #nginx_config()
    #uwsgi_config()
    #supervisor_config()
    #redis_install()
    # TODO settings customization
    # sync_data() # Fails if settings are not correctly set
    

def update():
    initialize()
    pull()
    install_requirements()
    sync_data()  
      
def clone():
    initialize()
    with settings(warn_only='true'):
        local('mkdir -p  %s' % root_dir)
        with lcd (root_dir):
            local('pwd && git clone %s nodeshot' % git_repo)
        #pull()
        #create_virtual_env()
        #install_requirements()
        
def install_dependencies():
    initialize()
    # Next line to be purged and file should be in repository
    local ('cp /var/www/nodeshot_deploy/dependencies.txt %s' % project_dir )
    with lcd(project_dir):
        local('cat dependencies.txt | xargs apt-get -y install')

def pull():
    initialize()
    with lcd (deploy_dir):
        local('pwd')
        local('git pull')

def create_virtual_env():
    with lcd (project_dir):
        local('virtualenv python')

def install_requirements():
    initialize()
    virtual_env = 'source python/bin/activate'
    pip_command = 'python/bin/pip install -r %srequirements.txt' % deploy_dir
    distribute_command = 'python/bin/pip install -U distribute'
    with lcd (project_dir):
        local( virtual_env + ' &&  ' + pip_command  + ' &&  ' + distribute_command)
 
def create_db():
    db_user = prompt('Set database user: ', default='nodeshot')
    local ('su - postgres -c "createdb nodeshot_local"')
    local ('su - postgres -c "psql nodeshot_local -c \'CREATE EXTENSION hstore;\'"')
    local ('su - postgres -c "psql nodeshot_local -c \'CREATE EXTENSION postgis;\'"')
    local ('su - postgres -c "psql nodeshot_local -c \'CREATE EXTENSION postgis_topology;\'"')
    local ('su - postgres -c "createuser %s -P -R -S -D"'  % db_user)
    local ('su - postgres -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE "nodeshot_local" to %s \'"' % db_user)
    
def sync_data():
    initialize()
    virtual_env = 'source python/bin/activate'
    sync_command = 'python manage.py syncdb && python manage.py migrate && python manage.py collectstatic'
    with lcd (project_dir):
        local( virtual_env + ' &&  ' + sync_command)
    
def nginx_config():
    initialize()
    server_name = prompt('Server name: ')
    nginx_dir = '/etc/nginx/ssl'
    local ('apt-get -y install nginx-full nginx-common openssl zlib-bin')
    local ('mkdir -p %s' % nginx_dir)
    with lcd (nginx_dir):
        local ('openssl req -new -x509 -nodes -out server.crt -keyout server.key')
    local('cp /etc/nginx/uwsgi_params /etc/nginx/sites-available/')
    local ('mkdir -p /var/www/nodeshot/public_html')
    # Next line to be purged and file should be in repository
    local ('cp /var/www/nodeshot_deploy/nodeshot.yourdomain.com /etc/nginx/sites-available/nodeshot.yourdomain.com')

    with lcd('/etc/nginx/sites-available'):
        local ('sed \'s/nodeshot.yourdomain.com/%s/g\' nodeshot.yourdomain.com > %s' % (server_name,server_name))
        local ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' %s ' % (project_dir,server_name))
        local ('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (server_name,server_name))
        
def uwsgi_config():
    initialize()
    local ('pip install uwsgi')
    # Next line to be purged and file should be in repository
    local ('cp /var/www/nodeshot_deploy/uwsgi.ini %s' % project_dir)
    with lcd (project_dir):
        local ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' uwsgi.ini ' % project_dir)
    
def supervisor_config():
    initialize()
    local('apt-get -y install supervisor')
    # Next lines to be purged and file should be in repository
    local ('cp /var/www/nodeshot_deploy/uwsgi.conf /etc/supervisor/conf.d/uwsgi.conf')
    local ('cp /var/www/nodeshot_deploy/celery.conf /etc/supervisor/conf.d/celery.conf')
    local ('cp /var/www/nodeshot_deploy/celery-beat.conf /etc/supervisor/conf.d/celery-beat.conf')
    with lcd ('/etc/supervisor/conf.d/'):
        local ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' uwsgi.conf ' % project_dir)
        local ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' celery.conf ' % project_dir)
        local ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' celery-beat.conf ' % project_dir)
    local('supervisorctl update')
    
def redis_install():
    initialize()
    virtual_env = 'source python/bin/activate'
    pip_command = 'python/bin/pip install -U celery[redis]'
    local('add-apt-repository ppa:chris-lea/redis-server')
    local('apt-get update')
    local('apt-get -y install redis-server')
    with lcd (project_dir):
        local( virtual_env + ' &&  ' + pip_command)
        
def start_server():
    initialize()
    with lcd (project_dir):
        local('touch log/ninux.error.log')
        local('chmod 666 log/ninux.error.log')
        local('service nginx restart && supervisorctl restart all')
        

    


    

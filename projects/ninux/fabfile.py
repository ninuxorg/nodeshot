from fabric.api import *
from django.utils.crypto import get_random_string



# Put host(s) configuration here or use -h switch on command line
# env.hosts = ''
# env.password = ''

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
secret_key = get_random_string(50, chars)
print secret_key
git_repo = 'https://github.com/ninuxorg/nodeshot.git'

#global root_dir
#global deploy_dir
#global project_dir

def initialize():
    install_dirs = ('root_dir','deploy_dir','project_dir')
    for install_dir in install_dirs:
        if install_dir not in globals():
            initialize_dirs()

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
    deploy_dir = '%snodeshot/' % root_dir
    project_dir = '%sprojects/ninux' % deploy_dir

def uninstall():
    initialize()
    with cd(project_dir):
        run('cat dependencies.txt | xargs apt-get -y purge')
    
def install():
    initialize()
    clone()
    install_dependencies()
    create_virtual_env()
    install_requirements()
    create_db()
    nginx_config()
    uwsgi_config()
    supervisor_config()
    redis_install()
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
        run('mkdir -p  %s' % root_dir)
        with cd (root_dir):
            run('git clone %s nodeshot' % git_repo  )
        with cd (deploy_dir):
            run ('git checkout deploy_test')
        #pull()
        #create_virtual_env()
        #install_requirements()
        
def install_dependencies():
    initialize()
    # Next line to be purged and file should be in repository
    #run ('cp /var/www/nodeshot_deploy/dependencies.txt %s' % project_dir )
    with cd(project_dir):
        run('cat dependencies.txt | xargs apt-get -y install')

def pull():
    initialize()
    with cd (deploy_dir):
        run('pwd')
        run('git pull')

def create_virtual_env():
    with cd (project_dir):
        run('virtualenv python')

def install_requirements():
    initialize()
    virtual_env = 'source python/bin/activate'
    pip_command = 'python/bin/pip install -r %srequirements.txt' % deploy_dir
    distribute_command = 'python/bin/pip install -U distribute'
    with cd (project_dir):
        run( virtual_env + ' &&  ' + pip_command  + ' &&  ' + distribute_command)
 
def create_db():
    initialize_db()
    run ('su - postgres -c "createdb nodeshot"')
    run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION hstore;\'"')
    run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis;\'"')
    run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis_topology;\'"')
    run ('su - postgres -c "createuser %s  -R -S -D "'  % db_user)
    run ('sudo -u postgres psql -U postgres -d postgres -c \"alter user %s with password \'%s\';\"' % (db_user,db_pass))
    run ('su - postgres -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE "nodeshot" to %s \'"' % db_user)
    
def sync_data():
    initialize()
    virtual_env = 'source python/bin/activate'
    sync_command = 'python manage.py syncdb && python manage.py migrate && python manage.py collectstatic'
    with cd (project_dir):
        run( virtual_env + ' &&  ' + sync_command)
    
def nginx_config():
    initialize()
    server_name = prompt('Server name: ')
    nginx_dir = '/etc/nginx/ssl'
    run ('apt-get -y install nginx-full nginx-common openssl zlib-bin')
    run ('mkdir -p %s' % nginx_dir)
    with cd (nginx_dir):
        run ('openssl req -new -x509 -nodes -out server.crt -keyout server.key')
    run('cp /etc/nginx/uwsgi_params /etc/nginx/sites-available/')
    run ('mkdir -p /var/www/nodeshot/public_html')
    
    run ('cp %s/nodeshot.yourdomain.com /etc/nginx/sites-available/nodeshot.yourdomain.com' % project_dir)

    with cd('/etc/nginx/sites-available'):
        run ('sed \'s/nodeshot.yourdomain.com/%s/g\' nodeshot.yourdomain.com > %s' % (server_name,server_name))
        run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' %s ' % (project_dir,server_name))
        run ('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (server_name,server_name))
        
def uwsgi_config():
    initialize()
    run ('pip install uwsgi')
    # Next line to be purged and file should be in repository
    #run ('cp /var/www/nodeshot_deploy/uwsgi.ini %s' % project_dir)
    with cd (project_dir):
        run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' uwsgi.ini ' % project_dir)
    
def supervisor_config():
    initialize()
    run('apt-get -y install supervisor')
    # Next lines to be purged and file should be in repository
    #run ('cp /var/www/nodeshot_deploy/uwsgi.conf /etc/supervisor/conf.d/uwsgi.conf')
    #run ('cp /var/www/nodeshot_deploy/celery.conf /etc/supervisor/conf.d/celery.conf')
    #run ('cp /var/www/nodeshot_deploy/celery-beat.conf /etc/supervisor/conf.d/celery-beat.conf')
    with cd ('/etc/supervisor/conf.d/'):
        run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' uwsgi.conf ' % project_dir)
        run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' celery.conf ' % project_dir)
        run ('sed -i \'s#/var/www/nodeshot/projects/ninux#%s#g\' celery-beat.conf ' % project_dir)
    run('supervisorctl update')
    
def redis_install():
    initialize()
    virtual_env = 'source python/bin/activate'
    pip_command = 'python/bin/pip install -U celery[redis]'
    run('add-apt-repository ppa:chris-lea/redis-server')
    run('apt-get update')
    run('apt-get -y install redis-server')
    with cd (project_dir):
        run( virtual_env + ' &&  ' + pip_command)
        
def start_server():
    initialize()
    with cd (project_dir):
        run('touch log/ninux.error.log')
        run('chmod 666 log/ninux.error.log')
        run('service nginx restart && supervisorctl restart all')
        

    


    

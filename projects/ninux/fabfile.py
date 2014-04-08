from fabric.api import *
#from fabric.api import local

env.hosts = 'root@nodeshot-deploy'
env.password = 'stefano'
root_dir = '/var/www/'
deploy_dir = '/var/www/nodeshot'
git_repo = 'https://github.com/ninuxorg/nodeshot.git'

#
#def local():
#    "Use the local virtual server"
#    hosts = ['localhost']


def test():
        run('uname -s')
      
def clone():    
    with settings(warn_only='true'):
        run('mkdir -p  %s' % root_dir)
        with cd (root_dir):
            run('git clone %s nodeshot' % git_repo)
        pull()
        create_virtual_env()
        install_requirements()

def pull():
    with cd (deploy_dir):
        run('pwd')
        run('git pull')

def create_virtual_env():
    with cd (deploy_dir):
        run('cd projects/ninux && virtualenv python')

def install_requirements():
    virtual_env = 'source python/bin/activate'
    pip_command = 'python/bin/pip install -r /var/www/nodeshot/requirements.txt'
    distribute_command = 'python/bin/pip install -U distribute'
    with cd ('%s/projects/ninux' % deploy_dir):
        run ('pwd')
        run( virtual_env + ' &&  ' + pip_command  + ' &&  ' + distribute_command)
 
def create_db():
    db_user = prompt('Set database user: ', default='nodeshot')
    #db_password = prompt('Specify favorite dish: ', 'dish', default='spam & eggs')
    run ('su - postgres -c "createdb nodeshot"')
    run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION hstore;\'"')
    run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis;\'"')
    run ('su - postgres -c "psql nodeshot -c \'CREATE EXTENSION postgis_topology;\'"')
    run ('su - postgres -c "createuser %s -P -R -S -D"'  % db_user)
    run ('su - postgres -c "psql -c \'GRANT ALL PRIVILEGES ON DATABASE "nodeshot" to %s \'"' % db_user)
    
def nginx_config():
    server_name = prompt('Server name: ')
    nginx_dir = '/etc/nginx/ssl'
    run ('apt-get -y install nginx-full nginx-common openssl zlib-bin')
    run ('mkdir %s' % nginx_dir)
    with cd (nginx_dir):
        run ('openssl req -new -x509 -nodes -out server.crt -keyout server.key')
    run('cp /etc/nginx/uwsgi_params /etc/nginx/sites-available/')
    run ('mkdir -p /var/www/nodeshot/public_html')
    run ('cp /var/www/nodeshot_deploy/nodeshot.yourdomain.com /etc/nginx/sites-available/nodeshot.yourdomain.com')
    with cd('/etc/nginx/sites-available'):
        run ('sed \'s/nodeshot.yourdomain.com/%s/g\' nodeshot.yourdomain.com > %s' % (server_name,server_name))
        run ('ln -s /etc/nginx/sites-available/nodeshot.yourdomain.com /etc/nginx/sites-enabled/%s' % server_name)
        #run('serv')
    

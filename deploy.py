import os
import pwd
import sys
import subprocess


def django_debug():
    os.environ['DJANGO_DEBUG_BOOL'] = 'False'
    
    return True

def depends():
    try:
        python_version = subprocess.check_output(['python3', '--version'], stderr=subprocess.STDOUT).decode()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] Python3 not installed")
        sys.exit(1)
    try:
        result = subprocess.run(['dpkg', '-l', 'python3.12-venv'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[+] python3.12-venv installed")
        else:
            print("[-] python3.12-venv not installed")
            sys.exit(1)
    except FileNotFoundError:
        print("Looks like is not Debian dist")
    
    try:
        pip_version = subprocess.check_output(['pip3', '--version'], stderr=subprocess.STDOUT).decode()
        print(f"[+] pip installed: {pip_version.split()[1]}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] pip not installed")
        sys.exit(1)
    
    if not os.path.exists('venv'):
        subprocess.run(['python3', '-m', 'venv', 'venv'], check=True)
        print("[+] Virtual environment created")
    else:
        print("[+] Virtual environment already exists")
    
    venv_pip = 'venv/bin/pip'
    if sys.platform == 'win32':
        venv_pip = 'venv\\Scripts\\pip'
    
    if os.path.exists('requirements.txt'):
        subprocess.run([venv_pip, 'install', '-r', 'requirements.txt'], check=True)
        print("[+] Dependencies installed")
    else:
        print("[-] requirements.txt not found")
    
    print("[+][+][+] All python depends are installed")

    return True


def trash():
    os.system('rm /etc/nginx/sites-available/default')
    os.system('rm /etc/nginx/sites-enabled/default')

    return True

def reload_all(domain):
    os.system(f'systemctl daemon-reload')
    os.system(f'systemctl enable {domain}.service')
    os.system(f'systemctl start {domain}.service')
    os.system('nginx -t')

    return True

def nginx(domain):
    config_data = {
        'path_to_static': os.path.join(os.getcwd(), 'present', 'static'),
        'path_to_media': os.path.join(os.getcwd(), 'media'),
        'project_path': os.getcwd(),
        'domain_1': domain
    }
    
    with open('nginx.art', 'r', encoding='utf-8') as f:
        config = f.read()
    
    for key, value in config_data.items():
        placeholder = f'%{key}%'
        config = config.replace(placeholder, value)
    
    nginx_available = f'/etc/nginx/sites-available/{domain}'
    nginx_enabled = f'/etc/nginx/sites-enabled/{domain}'
    
    with open(nginx_available, 'w', encoding='utf-8') as f:
        f.write(config)
    
    if os.path.exists(nginx_enabled):
        os.remove(nginx_enabled)
    os.symlink(nginx_available, nginx_enabled)
    
    return True

def service(domain):
    stat_info = os.stat(os.getcwd())
    uid = stat_info.st_uid
    username = pwd.getpwuid(uid).pw_name
    
    config_data = {
        'project_path': os.getcwd(),
        'venv_path': os.path.join(os.getcwd(), 'venv', 'bin', 'gunicorn'),
        'wsgi_module': 'base_app.wsgi:application',
        'username': username,
        'domain_1': domain,
        'service_name': f'{domain}.service'
    }
    
    with open('service.art', 'r', encoding='utf-8') as f:
        service_config = f.read()
    
    for key, value in config_data.items():
        placeholder = f'%{key}%'
        service_config = service_config.replace(placeholder, str(value))
    
    service_path = f'/etc/systemd/system/{config_data["service_name"]}'
    
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(service_config)
    
    return True

def check_files(domain):
    files_to_check = [
        f'/etc/nginx/sites-available/{domain}',
        f'/etc/nginx/sites-enabled/{domain}',
        f'/etc/systemd/system/{domain}.service'
    ]
    
    missing_files = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            pass
        else:
            print(f"[-] {file_path} missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"[-] Missing files: {', '.join(missing_files)}")
        sys.exit(1)
    
    try:
        if os.path.islink(files_to_check[1]):
            pass
        else:
            print(f"[-] {files_to_check[1]} is not a symlink")
            sys.exit(1)
    except:
        pass
    
    nginx_test = os.system('nginx -t > /dev/null 2>&1')
    if nginx_test == 0:
        pass
    else:
        print("[-] Nginx configuration test failed")
        sys.exit(1)
    
    return True
        

if __name__ == '__main__':
    domain = input('Enter domain (without www): ')

    if not domain:
        print("[-] Domain is required")
        sys.exit(1)

    domain = domain.replace('.', '')

    check = all([
        depends(),
        trash(),
        django_debug(),
        service(domain),
        nginx(domain),
        check_files(domain),
        reload_all(domain)
    ])
    if check:
        print('Site is deployed!')

    

    

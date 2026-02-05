import os
import pwd
import sys
import subprocess
import socket


def django_setts(domain):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Error getting IP: {e}")
        ip_address = '127.0.0.1'
    
    service_file = f'/etc/systemd/system/{domain}.service'
    
    if os.path.exists(service_file):
        with open(service_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if not line.strip().startswith('Environment='):
                new_lines.append(line)
        
        final_lines = []
        for line in new_lines:
            final_lines.append(line)
            if line.strip() == '[Service]':
                final_lines.append('Environment=DJANGO_DEBUG_BOOL=False')
                final_lines.append('Environment=DJANGO_IP_ADDRESSING=True')
                final_lines.append(f'Environment=DJANGO_IP_ADDRESS={ip_address}')
                final_lines.append('Environment=DJANGO_DOMAINING=True')
                final_lines.append(f'Environment=DJANGO_DOMAIN_NAME={domain}')
        
        with open(service_file, 'w') as f:
            f.write('\n'.join(final_lines))
        
        os.system(f'systemctl daemon-reload')
        os.system(f'systemctl restart {domain}.service')
        print(f"[+] Django settings updated in systemd: IP={ip_address}, Domain={domain}")
    
    return True

def django_full_setup():

    manage_path = os.path.join(os.getcwd(), 'base_app', 'manage.py')
    python_path = os.path.join(os.getcwd(), 'venv', 'bin', 'python')
    base_dir = os.path.join(os.getcwd(), 'base_app')
    
    mig_dir = os.path.join(base_dir, 'present', 'migrations')
    mig_init = os.path.join(mig_dir, '__init__.py')
    
    if not os.path.exists(mig_dir):
        os.makedirs(mig_dir, exist_ok=True)
        print(f"[+] Created directory: {mig_dir}")
    
    if not os.path.exists(mig_init):
        with open(mig_init, 'w') as f:
            f.write('')
        print(f"[+] Created: {mig_init}")
    
    commands = [
        ['makemigrations', 'present'],
        ['migrate', 'present'],
        ['migrate'],
    ]
    
    for cmd in commands:
        print(f"[+] Running: python manage.py {' '.join(cmd)}")
        try:
            result = subprocess.run(
                [python_path, manage_path] + cmd,
                cwd=base_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"STDOUT: {result.stdout[:200]}")
            if result.stderr:
                print(f"STDERR: {result.stderr[:200]}")
        except Exception as e:
            print(f"[-] Error: {e}")
    
    print("[+] Collecting static files...")
    subprocess.run(
        [python_path, manage_path, 'collectstatic', '--noinput'],
        cwd=base_dir,
        capture_output=True,
        text=True
    )

    print("[+] Creating superuser...")
    
    cmd = '''from django.contrib.auth import get_user_model; User = get_user_model(); username = "FatheR_5XU7"; password = "ArIaFk74"; print("Creating superuser..."); import sys; sys.stdout.flush(); '''
    cmd += '''if not User.objects.filter(username=username).exists(): User.objects.create_superuser(username, "", password); print("Created"); else: print("Exists")'''
    
    os.system(f'echo \'{cmd}\' | {python_path} {manage_path} shell')
    
    print("[+] Superuser setup completed")
    
    static_dir = os.path.join(base_dir, 'staticfiles')
    if os.path.exists(static_dir):
        os.system(f"chown -R www-data:www-data {static_dir}")
        os.system(f"chmod -R 755 {static_dir}")
        print(f"[+] Fixed permissions for static files")

    print("[+] Django setup completed")

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
    os.system('systemctl reload nginx')

    return True

def nginx(domain):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
    except:
        hostname = socket.gethostname()
        server_ip = socket.gethostbyname(hostname)
    
    config_data = {
        'path_to_static': os.path.join(os.getcwd(), 'base_app', 'staticfiles'),
        'path_to_media': os.path.join(os.getcwd(), 'media'),
        'project_path': os.getcwd(),
        'domain_1': domain,
        'server_ip': server_ip
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
    

    print("[+] Fixing permissions for web access...")
    

    static_dir = config_data['path_to_static']
    if os.path.exists(static_dir):
        os.system(f"chown -R www-data:www-data {static_dir}")
        os.system(f"chmod -R 755 {static_dir}")
        print(f"[+] Fixed permissions for: {static_dir}")
    

    media_dir = config_data['path_to_media']
    if os.path.exists(media_dir):
        os.system(f"chown -R www-data:www-data {media_dir}")
        os.system(f"chmod -R 755 {media_dir}")
        print(f"[+] Fixed permissions for: {media_dir}")
    

    project_root = config_data['project_path']
    current_dir = project_root
    chain_fixed = []
    

    while current_dir != '/':
        if os.path.exists(current_dir):
            os.system(f"chmod +x {current_dir}")
            chain_fixed.append(current_dir)
        current_dir = os.path.dirname(current_dir)
    
    print(f"[+] Added execute permission to {len(chain_fixed)} directories in path")

    os.system("nginx -t")
    os.system("systemctl reload nginx")
    
    print(f"[+] Nginx configured for domain: {domain}, IP: {server_ip}")
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
        service(domain),
        nginx(domain),
        django_setts(domain),
        django_full_setup(),
        check_files(domain),
        reload_all(domain)
    ])
    if check:
        print('Site is deployed!')

    

    

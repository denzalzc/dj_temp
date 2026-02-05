import os
import sys

def drop_site():
    domain = input("Enter domain: ").strip()
    
    if not domain:
        print("[-] Domain is required")
        sys.exit(1)

    os.environ['DJANGO_DEBUG_BOOL'] = 'True'
    
    service_name = f"{domain}.service"
    print(f"[+] Stopping service {service_name}...")
    os.system(f"systemctl stop {service_name}")
    os.system(f"systemctl disable {service_name}")
    
    service_path = f"/etc/systemd/system/{service_name}"
    if os.path.exists(service_path):
        os.remove(service_path)
        print(f"[+] Removed {service_path}")

    nginx_available = f"/etc/nginx/sites-available/{domain}"
    nginx_enabled = f"/etc/nginx/sites-enabled/{domain}"
    
    if os.path.exists(nginx_enabled):
        os.remove(nginx_enabled)
        print(f"[+] Removed {nginx_enabled}")
    
    if os.path.exists(nginx_available):
        os.remove(nginx_available)
        print(f"[+] Removed {nginx_available}")
    
    os.system("systemctl daemon-reload")
    os.system("systemctl restart nginx")
    
    print(f"[+][+][+] Site {domain} successfully undeployed")
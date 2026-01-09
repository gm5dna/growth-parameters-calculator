# Deployment Guide: Growth Parameters Calculator

This guide will help you deploy the Growth Parameters Calculator to `growth.gm5dna.com` using a Proxmox LXC container and Cloudflare Tunnel.

## Overview

- **Platform**: Proxmox LXC Container
- **Operating System**: Ubuntu 22.04 LTS (recommended)
- **Web Server**: Nginx (reverse proxy)
- **Application Server**: Gunicorn (WSGI server for Flask)
- **Domain Access**: Cloudflare Tunnel (secure, no port forwarding required)
- **Domain**: growth.gm5dna.com

---

## Part 1: Create LXC Container in Proxmox

### 1.1 Download Ubuntu Template

In Proxmox web interface:
1. Select your storage (e.g., `local`)
2. Go to **CT Templates**
3. Click **Templates**
4. Download **ubuntu-22.04-standard**

### 1.2 Create the LXC Container

1. Click **Create CT** in Proxmox
2. Configure the container:

**General:**
- **CT ID**: Choose an available ID (e.g., 200)
- **Hostname**: `growth-app`
- **Password**: Set a strong root password
- ✓ **Unprivileged container** (recommended for security)

**Template:**
- **Storage**: Select where you downloaded the template
- **Template**: ubuntu-22.04-standard

**Root Disk:**
- **Disk size**: 8 GB (sufficient for this application)

**CPU:**
- **Cores**: 2 (adequate for Flask app)

**Memory:**
- **Memory (MiB)**: 2048 (2 GB)
- **Swap (MiB)**: 512

**Network:**
- **Bridge**: vmbr0 (or your network bridge)
- **IPv4**: DHCP or Static (note the IP address)
- **IPv6**: DHCP or leave blank

3. Click **Finish** to create the container
4. **Start** the container

### 1.3 Initial Container Setup

Access the container console from Proxmox and run:

```bash
# Update system packages
apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone Europe/London  # Adjust to your timezone

# Install essential packages
apt install -y curl wget git nano sudo
```

---

## Part 2: Install Application Dependencies

### 2.1 Install Python and Required Packages

```bash
# Install Python 3 and pip
apt install -y python3 python3-pip python3-venv

# Install Nginx
apt install -y nginx

# Install system packages required by rcpchgrowth
apt install -y build-essential python3-dev
```

### 2.2 Create Application User

```bash
# Create a dedicated user for the application
useradd -m -s /bin/bash growthapp
```

---

## Part 3: Deploy the Application

### 3.1 Upload Application Files

From your local machine, copy the application to the container:

```bash
# From your Mac, replace <CONTAINER_IP> with actual IP
cd "/Users/stuart/Documents/working/coding/growth app"
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.claude' \
  ./ root@<CONTAINER_IP>:/opt/growth-app/
```

**Alternative**: If rsync isn't available, you can:
1. Push the code to GitHub
2. Clone it on the container: `git clone https://github.com/yourusername/growth-app.git /opt/growth-app`

### 3.2 Set Up Application on Container

SSH into the container and run:

```bash
# Set ownership
chown -R growthapp:growthapp /opt/growth-app

# Switch to application user
su - growthapp

# Navigate to application directory
cd /opt/growth-app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn

# Test the application
python app.py
# Press Ctrl+C to stop after verifying it works

# Exit back to root
exit
```

---

## Part 4: Configure Gunicorn Service

### 4.1 Create Gunicorn Configuration

Create `/opt/growth-app/gunicorn_config.py`:

```bash
nano /opt/growth-app/gunicorn_config.py
```

Add the following content:

```python
# Gunicorn configuration file
bind = "127.0.0.1:8080"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/growth-app/access.log"
errorlog = "/var/log/growth-app/error.log"
loglevel = "info"

# Process naming
proc_name = "growth-app"

# Server mechanics
daemon = False
pidfile = "/var/run/growth-app.pid"
user = "growthapp"
group = "growthapp"
```

### 4.2 Create Log Directory

```bash
mkdir -p /var/log/growth-app
chown growthapp:growthapp /var/log/growth-app
```

### 4.3 Create Systemd Service

Create `/etc/systemd/system/growth-app.service`:

```bash
nano /etc/systemd/system/growth-app.service
```

Add the following content:

```ini
[Unit]
Description=Growth Parameters Calculator
After=network.target

[Service]
Type=simple
User=growthapp
Group=growthapp
WorkingDirectory=/opt/growth-app
Environment="PATH=/opt/growth-app/venv/bin"
ExecStart=/opt/growth-app/venv/bin/gunicorn -c /opt/growth-app/gunicorn_config.py app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 4.4 Enable and Start the Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable growth-app

# Start the service
systemctl start growth-app

# Check status
systemctl status growth-app
```

---

## Part 5: Configure Nginx Reverse Proxy

### 5.1 Create Nginx Configuration

Create `/etc/nginx/sites-available/growth-app`:

```bash
nano /etc/nginx/sites-available/growth-app
```

Add the following content:

```nginx
server {
    listen 80;
    server_name growth.gm5dna.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/growth-app-access.log;
    error_log /var/log/nginx/growth-app-error.log;

    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /opt/growth-app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5.2 Enable the Site

```bash
# Create symbolic link to enable site
ln -s /etc/nginx/sites-available/growth-app /etc/nginx/sites-enabled/

# Remove default site if it exists
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

---

## Part 6: Set Up Cloudflare Tunnel

### 6.1 Install Cloudflared

```bash
# Add Cloudflare GPG key
mkdir -p /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null

# Add Cloudflare repository
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/cloudflared.list

# Update and install
apt update
apt install -y cloudflared
```

### 6.2 Authenticate Cloudflared

```bash
# Login to Cloudflare
cloudflared tunnel login
```

This will output a URL. Open it in a browser and:
1. Select your domain (`gm5dna.com`)
2. Authorise the tunnel

A certificate will be downloaded to `/root/.cloudflared/cert.pem`

### 6.3 Create a Tunnel

```bash
# Create the tunnel
cloudflared tunnel create growth-app

# Note the Tunnel ID from the output
# It will be a UUID like: 12345678-1234-1234-1234-123456789abc
```

### 6.4 Configure the Tunnel

Create `/root/.cloudflared/config.yml`:

```bash
nano /root/.cloudflared/config.yml
```

Add the following (replace `TUNNEL_ID` with your actual tunnel ID):

```yaml
tunnel: TUNNEL_ID
credentials-file: /root/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: growth.gm5dna.com
    service: http://localhost:80
  - service: http_status:404
```

### 6.5 Configure DNS

```bash
# Create DNS record for the tunnel (replace TUNNEL_ID)
cloudflared tunnel route dns growth-app growth.gm5dna.com
```

This creates a CNAME record pointing `growth.gm5dna.com` to your tunnel.

### 6.6 Run Tunnel as a Service

```bash
# Install the tunnel as a service
cloudflared service install

# Start the service
systemctl start cloudflared

# Enable on boot
systemctl enable cloudflared

# Check status
systemctl status cloudflared
```

---

## Part 7: Verify Deployment

### 7.1 Check Services

```bash
# Check all services are running
systemctl status growth-app
systemctl status nginx
systemctl status cloudflared

# Check if application is responding locally
curl http://localhost:80
```

### 7.2 Test from Browser

1. Open your browser
2. Navigate to `https://growth.gm5dna.com`
3. You should see the Growth Parameters Calculator
4. Cloudflare automatically provides SSL/TLS

### 7.3 Check Logs

If there are issues:

```bash
# Application logs
journalctl -u growth-app -f

# Gunicorn logs
tail -f /var/log/growth-app/error.log

# Nginx logs
tail -f /var/log/nginx/growth-app-error.log

# Cloudflared logs
journalctl -u cloudflared -f
```

---

## Part 8: Maintenance and Updates

### 8.1 Update the Application

```bash
# SSH into container
ssh root@<CONTAINER_IP>

# Pull latest code (if using git)
cd /opt/growth-app
git pull

# Or upload new files via rsync from your Mac
# rsync -avz --exclude 'venv' ./ root@<CONTAINER_IP>:/opt/growth-app/

# Switch to app user and update dependencies
su - growthapp
cd /opt/growth-app
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Exit and restart service
exit
systemctl restart growth-app
```

### 8.2 Monitor Resources

```bash
# Check memory and CPU usage
htop

# Check disk usage
df -h

# Check service logs
journalctl -u growth-app --since "1 hour ago"
```

### 8.3 Backup

```bash
# Create backup directory on Proxmox host
mkdir -p /var/backups/growth-app

# Backup application (from Proxmox host)
pct exec <CT_ID> -- tar -czf /tmp/growth-app-backup.tar.gz /opt/growth-app
pct pull <CT_ID> /tmp/growth-app-backup.tar.gz /var/backups/growth-app/growth-app-$(date +%Y%m%d).tar.gz
```

---

## Part 9: Security Hardening (Optional but Recommended)

### 9.1 Enable Firewall

```bash
# Install ufw
apt install -y ufw

# Allow SSH (if using it)
ufw allow 22/tcp

# Allow HTTP/HTTPS (only if needed for local access)
# ufw allow 80/tcp
# ufw allow 443/tcp

# Enable firewall
ufw enable
```

Note: With Cloudflare Tunnel, you don't need to open ports 80/443 to the internet.

### 9.2 Cloudflare Additional Security

In Cloudflare Dashboard (cloudflare.com):

1. Go to **Security** → **WAF**
   - Enable Web Application Firewall
   - Set security level to "Medium" or "High"

2. Go to **SSL/TLS**
   - Set mode to "Full (strict)"

3. Go to **Speed** → **Optimization**
   - Enable Auto Minify for HTML, CSS, JS
   - Enable Brotli compression

4. Go to **Caching**
   - Set Browser Cache TTL appropriately
   - Create cache rules if needed

---

## Part 10: Troubleshooting

### Application Won't Start

```bash
# Check Python errors
su - growthapp
cd /opt/growth-app
source venv/bin/activate
python app.py

# Check dependencies
pip list
```

### Nginx Errors

```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
cloudflared tunnel info growth-app

# Restart tunnel
systemctl restart cloudflared

# Check logs
journalctl -u cloudflared -n 100
```

### Can't Access Website

1. Check DNS propagation: `nslookup growth.gm5dna.com`
2. Verify tunnel is running: `systemctl status cloudflared`
3. Check Nginx is running: `systemctl status nginx`
4. Check app is running: `systemctl status growth-app`
5. Test locally: `curl http://localhost:80`

---

## Summary of Services

| Service | Purpose | Port | Status Command |
|---------|---------|------|----------------|
| growth-app | Flask application via Gunicorn | 8080 (localhost) | `systemctl status growth-app` |
| nginx | Reverse proxy | 80 (localhost) | `systemctl status nginx` |
| cloudflared | Cloudflare Tunnel | N/A | `systemctl status cloudflared` |

---

## Useful Commands Quick Reference

```bash
# Restart application
systemctl restart growth-app

# View application logs
journalctl -u growth-app -f

# Reload Nginx configuration
systemctl reload nginx

# Restart Cloudflare Tunnel
systemctl restart cloudflared

# Check all services
systemctl status growth-app nginx cloudflared

# Access container from Proxmox host
pct enter <CT_ID>
```

---

## Notes

- **No port forwarding required**: Cloudflare Tunnel handles all external access
- **Automatic SSL**: Cloudflare provides SSL certificates automatically
- **DDoS protection**: Cloudflare provides built-in protection
- **Analytics**: View traffic stats in Cloudflare Dashboard
- **Zero trust**: Cloudflare Tunnel uses outbound connections only (more secure)

---

## Additional Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/latest/deploying/)

FROM typecho:0.3

# 安装PHP扩展和依赖
RUN apt-get update && apt-get install -y \
        libcurl4-openssl-dev \
        libssl-dev \
        libz-dev \
        libzip-dev \
        libonig-dev \
        default-mysql-client \
    && docker-php-ext-install \
        curl \
        mbstring \
        json \
        zip \
        mysqli \
        pdo_mysql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 启用Apache模块
RUN a2enmod ssl && a2enmod rewrite

# 创建SSL目录
RUN mkdir -p /var/www/html/ssl && \
    chown -R www-data:www-data /var/www/html

# 配置Apache虚拟主机
RUN echo '<VirtualHost *:80>\n\
    ServerAdmin webmaster@localhost\n\
    DocumentRoot /var/www/html\n\
    RewriteEngine On\n\
    RewriteCond %{HTTPS} off\n\
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]\n\
</VirtualHost>\n\
\n\
<VirtualHost *:443>\n\
    ServerAdmin webmaster@localhost\n\
    DocumentRoot /var/www/html\n\
    SSLEngine on\n\
    SSLCertificateFile /var/www/html/ssl/cert.crt\n\
    SSLCertificateKeyFile /var/www/html/ssl/cert.key\n\
    ErrorLog ${APACHE_LOG_DIR}/error.log\n\
    CustomLog ${APACHE_LOG_DIR}/access.log combined\n\
    <Directory /var/www/html>\n\
        Options Indexes FollowSymLinks\n\
        AllowOverride All\n\
        Require all granted\n\
    </Directory>\n\
</VirtualHost>' > /etc/apache2/sites-available/000-default.conf

# 启用SSL站点
RUN ln -sf /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-enabled/000-default.conf

# 设置工作目录
WORKDIR /var/www/html
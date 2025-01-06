FROM php:7.4-apache

# 安装扩展和工具
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-install -j$(nproc) mysqli pdo_mysql

# PHP配置
RUN { \
    echo 'memory_limit = 256M'; \
    echo 'upload_max_filesize = 100M'; \
    echo 'post_max_size = 100M'; \
    echo 'max_execution_time = 300'; \
    } > /usr/local/etc/php/conf.d/custom.ini

# Apache配置
RUN a2enmod rewrite \
    && echo "ServerName localhost" > /etc/apache2/conf-available/servername.conf \
    && a2enconf servername

# 环境变量设置
ENV APACHE_RUN_USER=www-data \
    APACHE_RUN_GROUP=www-data \
    APACHE_LOG_DIR=/var/log/apache2 \
    APACHE_LOCK_DIR=/var/lock/apache2 \
    APACHE_PID_FILE=/var/run/apache2/apache2.pid \
    APACHE_RUN_DIR=/var/run/apache2

# 创建必要目录和设置权限
RUN mkdir -p /var/run/apache2 /var/lock/apache2 \
    && chown -R www-data:www-data /var/run/apache2 /var/lock/apache2 /var/www/html

WORKDIR /var/www/html

# 使用supervisord管理进程
RUN apt-get update && apt-get install -y supervisor \
    && mkdir -p /var/log/supervisor \
    && { \
        echo '[supervisord]'; \
        echo 'nodaemon=true'; \
        echo '[program:apache2]'; \
        echo 'command=apache2-foreground'; \
        echo 'stdout_logfile=/dev/stdout'; \
        echo 'stdout_logfile_maxbytes=0'; \
        echo 'stderr_logfile=/dev/stderr'; \
        echo 'stderr_logfile_maxbytes=0'; \
    } > /etc/supervisor/conf.d/apache2.conf


#自用的博客搭建。
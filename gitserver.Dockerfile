FROM ubuntu:18.04
RUN apt update 2>/dev/null
RUN apt install -y git apache2 apache2-utils 2>/dev/null
RUN a2enmod env cgi alias rewrite
RUN mkdir /var/www/git
RUN chown -Rfv www-data:www-data /var/www/git
COPY ./etc/git.conf /etc/apache2/sites-available/git.conf
COPY ./etc/git-create-repo.sh /usr/bin/mkrepo
RUN chmod +x /usr/bin/mkrepo
RUN a2dissite 000-default.conf
RUN a2ensite git.conf
RUN git config --system http.receivepack true
RUN git config --system http.uploadpack true
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
# Python package management and basic dependencies
RUN apt-get install -y curl python3.7 python3.7-dev python3.7-distutils

# Register the version in alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.7

# Upgrade pip to latest version
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py
RUN mkdir /app
RUN mkdir /app/clones
RUN mkdir /app/repos
COPY ./api/* /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
ENV CLONE_MASTER /app/clones
ENV REPO_MASTER /app/repos
ENTRYPOINT ["python"]
CMD ["main_api.py"]
EXPOSE 80/tcp
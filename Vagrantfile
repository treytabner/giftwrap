# encoding: UTF-8

GIFTWRAP_MANIFEST = ENV['GIFTWRAP_MANIFEST'] || 'examples/manifest.yml'
GIFTWRAP_ARGS = ENV['GIFTWRAP_ARGS'] || '-t package'
GIFTWRAP_BUILDBOX_NAME = ENV['GIFTWRAP_BUILDBOX_NAME'] || 'ursula-precise'
GIFTWRAP_BUILDBOX_URL = ENV['GIFTWRAP_BUILDBOX_URL'] || 'http://apt.openstack.blueboxgrid.com/vagrant/ursula-precise.box'
GIFTWRAP_POSTBUILD_SCRIPT = ENV['GIFTWRAP_POSTBUILD_SCRIPT'] || ""

if ENV['GIFTWRAP_SECURITY_GROUPS']
  GIFTWRAP_SECURITY_GROUPS = ENV['GIFTWRAP_SECURITY_GROUPS'].split(",")
else
  GIFTWRAP_SECURITY_GROUPS = []
end

ENV['VAGRANT_DEFAULT_PROVIDER'] = 'virtualbox'

Vagrant.configure('2') do |config|
  config.vm.box = GIFTWRAP_BUILDBOX_NAME
  config.vm.box_url = GIFTWRAP_BUILDBOX_URL

  config.vm.provider :virtualbox do |vbox, override|
    vbox.memory = 2048
    vbox.cpus = 2
  end

  config.vm.provider :openstack do |os, override|
    os.openstack_auth_url    = "#{ENV['OS_AUTH_URL']}/tokens"
    os.username              = ENV['OS_USERNAME']
    os.password              = ENV['OS_PASSWORD']
    os.tenant_name           = ENV['OS_TENANT_NAME']
    os.flavor                = 'm1.small'
    os.image                 = 'ubuntu-12.04'
    os.openstack_network_url = ENV['OS_NEUTRON_URL']
    os.networks              = ['internal']
    os.floating_ip_pool      = 'external'
    os.security_groups    = GIFTWRAP_SECURITY_GROUPS
    os.rsync_exclude_paths   = []
    os.rsync_cvs_exclude     = false
    override.vm.box       = 'openstack'
    override.ssh.username = 'ubuntu'
  end

  config.vm.provision 'shell', inline: <<-EOF
    #!/bin/bash
    set -x
    set -e
    if [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
    elif [ -f /etc/debian_version ]; then
        OS=Debian
    elif [ -f /etc/redhat-release ]; then
        OS=RedHat
    fi

    if [ "$OS" == "Debian" ] || [ "$OS" == "Ubuntu" ]; then
        /vagrant/scripts/prepare_debian.sh
    fi

    gem install --no-ri --no-rdoc fpm
    cd /vagrant
    python setup.py install
    giftwrap build -m #{GIFTWRAP_MANIFEST} #{GIFTWRAP_ARGS}

    if [ ! -z "#{GIFTWRAP_POSTBUILD_SCRIPT}" ]; then
        #{GIFTWRAP_POSTBUILD_SCRIPT}
    fi

  EOF

  config.vm.define 'giftwrap' do |c|
    c.vm.host_name = 'giftwrap'
  end
end

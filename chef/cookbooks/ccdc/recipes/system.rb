# Fix the locale
execute "create-locale" do
  command %Q{
    locale-gen en_US.UTF-8
  }
end

execute "set-locale" do
  command %Q{
    update-locale LANG=en_US.UTF-8
  }
end


# Load system dependencies with apt-get
node[:dependencies].each do |pkg|
    package pkg do
        :upgrade
    end
end


py_version = "#{node[:python_version][:major]}.#{node[:python_version][:minor]}.#{node[:python_version][:micro]}"

# Download new Python binary
remote_file "Python-#{py_version}.tgz" do
  source "https://www.python.org/ftp/python/#{py_version}/Python-#{py_version}.tgz"
  mode 0555
end


# Unpack
execute "unpack-python" do
  command "tar xfz Python-#{py_version}.tgz"
end


# Configure
execute "configure" do
  cwd "/Python-#{py_version}/"
  command "./configure --prefix /usr/local/lib/python#{py_version} --enable-ipv6"
end


# Build
execute "build" do
    cwd "/Python-#{py_version}/"
    command "sudo make"
end


# Install
execute "install" do
    cwd "/Python-#{py_version}/"
    command "sudo make altinstall"
end

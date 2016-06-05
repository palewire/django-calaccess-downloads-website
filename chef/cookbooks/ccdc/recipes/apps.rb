# Create the apps directory where everything will go
directory "/apps/" do
    owner node[:apps_user]
    group node[:apps_group]
    mode 0775
end

# Make the directory for the app
virtualenv "/apps/calaccess" do
    owner node[:apps_user]
    group node[:apps_group]
    mode 0775
end

# Make the directory for the django project
directory "/apps/calaccess/repo" do
    owner node[:apps_user]
    group node[:apps_group]
    mode 0775
end

remote_directory "/apps/calaccess/repo" do
  files_mode '0777'
  files_owner node[:app_user]
  mode '0777'
  owner node[:app_user]
  source "django"
end

# Install the virtualenv requirements
script "Install requirements" do
  interpreter "bash"
  user node[:apps_user]
  group node[:apps_group]
  code "/apps/calaccess/bin/pip install -r /apps/calaccess/repo/requirements.txt"
end

# Create the database user
script "Create database user" do
  interpreter "bash"
  user node[:apps_user]
  code <<-EOH
     mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO #{node[:db_user]}@'%' IDENTIFIED BY '#{node[:db_password]}'"
  EOH
  ignore_failure true
end

# Create the database
script "Create database" do
  interpreter "bash"
  user "ubuntu"
  code <<-EOH
    mysql -u #{node[:db_user]} -p#{node[:db_password]} -e "create database #{node[:db_name]}"; 
  EOH
end

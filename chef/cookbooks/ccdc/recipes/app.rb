# Create the apps directory where everything will go
directory "/apps/" do
    owner node[:apps_user]
    group node[:apps_group]
    mode 0775
end

# Make the directory for the app
virtualenv "/apps/#{node[:app][:name]}" do
    owner node[:apps_user]
    group node[:apps_group]
    mode 0775
end

# Make the directory for the django project
directory "/apps/#{node[:app][:name]}/repo" do
    owner node[:apps_user]
    group node[:apps_group]
    mode 0775
end

# Pull the git repo
git "/apps/#{node[:app][:name]}/repo"  do
  repository node[:app][:repo]
  reference "HEAD"
  revision node[:app][:branch]
  user node[:apps_user]
  group node[:apps_group]
  action :sync
end

# Install the virtualenv requirements
script "Install requirements" do
  interpreter "bash"
  user node[:apps_user]
  group node[:apps_group]
  code "/apps/#{node[:app][:name]}/bin/pip install -r /apps/#{node[:app][:name]}/repo/requirements.txt"
end

# create .secrets file from template
template "/apps/#{node[:app][:name]}/.secrets" do
  source "secrets.erb"
  mode 0555
  owner node[:apps_user]
  group node[:apps_group]
  variables({
    :aws_access_key_id => node[:aws_access_key_id],
    :aws_secret_access_key => node[:aws_secret_access_key],
    :db_host => node[:db_host],
    :db_password => node[:db_password]
  })
end
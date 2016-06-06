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

# Pull the git repo
git "/apps/#{node[:app][:name]}/repo"  do
  repository node[:app][:repo]
  reference "HEAD"
  revision node[:app][:branch]
  user node[:apps_user]
  group node[:apps_group]
  action :sync
end

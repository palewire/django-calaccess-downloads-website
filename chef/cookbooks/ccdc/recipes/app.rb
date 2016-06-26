# Create user and group
group node[:app][:group] do
    gid 101
end

user node[:app][:user] do 
    comment node[:app][:user]
    uid 102
    gid 101
    shell "/bin/bash"
    supports :manage_home => true
    home "/home/" + node[:app][:user]
end

group node[:app][:group] do
    gid 101
    members node[:app][:user]
end


# Make the user a superuser
template "/etc/sudoers" do
    source "sudoers.erb"
    mode 0440
    owner "root"
    group "root"
    variables({
        :user => node[:app][:user]
    })
end


# Create the apps directory where everything will go
directory "/apps/" do
    owner node[:app][:user]
    group node[:app][:group]
    mode 0775
end


# Make the directory for the app
virtualenv "/apps/#{node[:app][:name]}" do
    owner node[:app][:user]
    group node[:app][:group]
    mode 0775
end


# Make the directory for the django project
directory "/apps/#{node[:app][:name]}/repo" do
    owner node[:app][:user]
    group node[:app][:group]
    mode 0775
end


# Pull the git repo
git "/apps/#{node[:app][:name]}/repo"  do
    repository node[:app][:repo]
    reference "HEAD"
    revision node[:app][:branch]
    user node[:app][:user]
    group node[:app][:group]
    action :sync
end


# Install the virtualenv requirements
script "Install requirements" do
    interpreter "bash"
    user node[:app][:user]
    group node[:app][:group]
    code "/apps/#{node[:app][:name]}/bin/pip install -r /apps/#{node[:app][:name]}/repo/requirements.txt"
end

# CAW
cookbook_file "/etc/update-motd.d/01-bear" do
  source "motd/bear.sh"
  owner "root"
  group "root"
end

bash "chmod motd" do
  user "root"
  group "root"
  code "chmod a+x /etc/update-motd.d/01-bear"
end

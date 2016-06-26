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


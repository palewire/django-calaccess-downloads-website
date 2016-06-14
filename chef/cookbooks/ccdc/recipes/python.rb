# System wide python packages via apt
node[:ubuntu_python_packages].each do |pkg|
    package pkg do
        :upgrade
    end
end

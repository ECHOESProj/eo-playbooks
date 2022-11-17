
Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/focal64"
  config.vm.boot_timeout = 3000
  config.vm.define "eo-service"

  # Assuming this is run on WSL:
  # Access the VM with the Windows Machine.
  # Used to access Minio.
  # Set the IP to a free public IP on the Windows machine
#   config.vm.network :private_network, ip: "192.168.56.16"  # A free public IP address on the Windows host
  config.vm.network "forwarded_port", guest: 9000, host: 9000
  config.vm.network "forwarded_port", guest: 9001, host: 9001
  config.vm.network "forwarded_port", guest: 8888, host: 8888

#   config.vm.synced_folder "../", "/home/vagrant/echoes-local/"  # Assumes the rest of the code is in the parent dir

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--uartmode1", "disconnected"]
  end

  config.vm.provision "ansible" do |ansible|
      ansible.groups = {"servers_local" => ["eo-service"], "local" => ["eo-service"]}
      ansible.limit = "all"
      ansible.become = "yes"
      ansible.become_user = "vagrant"
      ansible.ask_vault_pass = true
      ansible.playbook = "site.yml"
  end

end

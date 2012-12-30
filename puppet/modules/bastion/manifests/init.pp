class bastion {

  host { $vpc_host:
    host_aliases => ["$vpc_host.local"],
    ip => "$ipaddress",
    ensure => present,
  }

  file { "/home/$user/.ssh/known_hosts":
    ensure => absent,
  }
}

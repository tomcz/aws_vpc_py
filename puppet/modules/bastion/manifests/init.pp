class bastion {

  host { "$hostname":
    ip => "$ipaddress",
    ensure => present,
  }

  file { "/home/$user/.ssh/known_hosts":
    ensure => absent,
  }
}

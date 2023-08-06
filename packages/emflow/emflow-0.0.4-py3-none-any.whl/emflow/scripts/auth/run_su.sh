#!/usr/bin/expect -f
#Usage: script.sh cmd user pass

set cmd [lindex $argv 0];
set user [lindex $argv 1];
set pass [lindex $argv 2];

#export LANGUAGE='en_US:en'

log_user 0

spawn su -c $cmd $user
expect {
  "Password: " {send "$pass\r"}
  "密码： " {send "$pass\r"}
  }

expect {
  "su: Authentication failure" {exit 1}
  "su：认证失败" {exit 1}
  '$ ' {exit 0}
  }

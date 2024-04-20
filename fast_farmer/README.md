Setup Ansible inventory file with harvesters

`nano inventory.ini`

```
[harvesters]
192.168.1.10
192.168.1.11
```

make sure ssh keys are copied to the ansible hosts
`ssh-copyid user@192.168.1.10`

copy latest version of `ff_giga` into templates folder
copy fast_farmer.yaml from `ff_giga init output`, saved in `~/.config/fast_farmer/fast_farmer.yaml` to templates
copy ca folder from `~/.chia/mainnet/config/ssl/ca/` to `templates`

run
`ansible-playbook fast.yml --become --become-user root -K -i inventory`

to restart
`ansible -m shell -a 'systemctl restart fast_farmer.service' --become --become-user root -K harvesters -i inventory`

to check status
`ansible -m shell -a 'systemctl status fast_farmer.service' --become --become-user root -K harvesters -i inventory`
or
`ansible -m shell -a 'journalctl -u fast_farmer.service --since "1 minute ago"' harvesters -i inventory`
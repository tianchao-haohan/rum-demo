curl -XPUT localhost:9200/_template/rum -d @apm_rum_template.json 

es_config:
1. sysctl -w vm.max_map_count=262144
    To set this value permanently, update the vm.max_map_count setting in /etc/sysctl.conf.
2. -Xms1g


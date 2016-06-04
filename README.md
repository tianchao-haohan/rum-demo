curl -XPUT localhost:9200/_template/rum -d @apm_rum_template.json 

es_config:
1. sysctl -w vm.max_map_count=262144
    To set this value permanently, update the vm.max_map_count setting in /etc/sysctl.conf.
2. -Xms1g

docker run --privileged -d --name elk -p 80:80 -p 9200:9200 -e ES_JAVA_OPTS="-Xms2g -Xmx2g" blacktop/elk:5.0-alpha

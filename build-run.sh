mvn -f controllers/onos-app/data-classification clean install -DskipTests -Dcheckstyle.skip
./run.sh
exit 0
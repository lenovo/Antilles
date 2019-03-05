# Ganglia-mond

Ganglia is a scalable, real-time monitoring and execution environment
with all execution requests and statistics expressed in an open
well-defined XML format.

This gmetad daemon aggregates monitoring data from several clusters
to form a monitoring grid. It also keeps metric history using influxdb.

antilles-ganglia-mond is a re-write of the original gmetad code (written in C)
with pluggable interface.
# Lab | Check the requirements

1. Docker is a requirement for all the exercises and the entire DevSecOps
   environment configuration, so depending on the operating system the `docker`
   packages need to be installed, [following the official instructions](https://docs.docker.com/engine/install/).

   The docker daemon must be in execution, check it by:

   ```console
   > systemctl status docker
   ● docker.service - Docker Application Container Engine
        Loaded: loaded (/lib/systemd/system/docker.service; disabled; vendor preset: enabled)
        Active: active (running) since Wed 2023-06-21 10:26:41 CEST; 4h 8min ago
   TriggeredBy: ● docker.socket
          Docs: https://docs.docker.com
      Main PID: 23750 (dockerd)
         Tasks: 122
        Memory: 2.0G
           CPU: 1min 29.063s
   ...
   ```

2. All the services deployed in this lab will run as containers on a host.
   This means that each service port will be published on the docker host, by
   using `--publish` option, that will make the port listen on `localhost` and
   any other interface on the host.
   To make services reachable between containers it is mandatory to use an IP
   different from `localhost` (`127.0.0.1`).
   The docker host should have an interface called `docker0`, and its IP address
   can be identified like this:

   ```console
   > ip address show dev docker0 | grep 'inet ' | awk '{print $2}'
   172.17.0.1/16
   ```

   This value must be used as a reference for the services configurations.

   NOTE: the IP address depends on the machine configuration, so you might want
   to chose a different IP. It is possible to list all the machine IP using the
   `ip address show` command.

# Exercise | SonarQube installation and configuration

1. Launch the SonarQube instance using the `sonarqube:latest` container image,
   exposing these ports (Host/Container):
   - 9000:9000

   ```console
   > docker run --detach \
     --name sonarqube \
     --publish 9000:9000 \
     sonarqube:latest
   ```

   Check the progresses, until the web interface comes up:

   ```console
   > docker logs -f sonarqube
   2023.06.20 14:36:58 INFO  app[][o.s.a.AppFileSystem] Cleaning or creating temp directory /opt/sonarqube/temp
   2023.06.20 14:36:58 INFO  app[][o.s.a.es.EsSettings] Elasticsearch listening on [HTTP: 127.0.0.1:9001, TCP: 127.0.0.1:38019]
   ...
   2023.06.20 14:37:33 INFO  app[][o.s.a.SchedulerImpl] SonarQube is operational
   ...
   ```

2. Log into SonarQube interface by using `admin`/`admin` credentials at [http://localhost:9000](http://localhost:9000)
   and the admin password as requested.

   Select the users section at [http://localhost:9000/admin/users](http://localhost:9000/admin/users)
   and under "Tokens" click in the icon.

   Create a token named "GitLab" leaving "30 days" as "Expires in" and take note
   of the value, which will be something like `squ_a37f1d4c60b980cb91fb5d4fb878d2b96be2ecb5`.

3. Move to the GitLab interface in the `CI/CD Settings` of `myproject` at:

   [http://localhost:8080/devsecops/myproject/-/settings/ci_cd](http://localhost:8080/devsecops/myproject/-/settings/ci_cd)

   Click `Expand` button of the `Variables` section, and add:

   - `SONARQUBE_HOST`: http://172.17.0.1:9000
   - `SONARQUBE_TOKEN`: squ_a37f1d4c60b980cb91fb5d4fb878d2b96be2ecb5

   The `SONARQUBE_HOST` refers to the IP of the docker host, check
   [DevSecOps_Requirements.md](DevSecOps_Requirements.md) to find out how to get it.

   Ensure that for the `SONARQUBE_TOKEN` variable the `Mask variable` option is
   selected.

5. Create a CI lab involving Sonarqube, by adding this `.gitlab-ci.yml` inside `myproject`:

   ```yaml
   stages:
     - sonarqube
   
   sonarqube_job:
     stage: sonarqube
     image: sonarsource/sonar-scanner-cli:latest
     script:
       - sonar-scanner
         -Dsonar.host.url=$SONARQUBE_HOST
         -Dsonar.login=$SONARQUBE_TOKEN
         -Dsonar.projectKey=myproject
     only:
       - main
   ```

   Commit and push the chage:

   ```console
   > git add .

   > git status
   On branch main
   Your branch is up to date with 'origin/main'.
   
   Changes to be committed:
     (use "git restore --staged <file>..." to unstage)
   	new file:   .gitlab-ci.yml
   
   > git commit -m "Add SonarQube stage to CI"
   [main 682a9b482669] Add SonarQube stage to CI
    1 file changed, 12 insertions(+)
    create mode 100644 .gitlab-ci.yml

   > git push
   Enumerating objects: 4, done.
   Counting objects: 100% (4/4), done.
   Delta compression using up to 16 threads
   Compressing objects: 100% (3/3), done.
   Writing objects: 100% (3/3), 458 bytes | 458.00 KiB/s, done.
   Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
   To ssh://localhost:2222/devsecops/myproject.git
      f38a63bbf9f6..682a9b482669  main -> main
   ```

   And then follow the progress from the GitLab interface.

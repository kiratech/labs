# Exercise | Install and configure Nexus

1. Launch the Nexus instance using the `sonatype/nexus3` container, exposing
   these ports (Host/Container):
   - 8081:8081
   - 5000:5000

   ```console
   > docker run --detach --publish 8081:8081 --publish 5000:5000 --name nexus sonatype/nexus3
   Unable to find image 'sonatype/nexus3:latest' locally
   latest: Pulling from sonatype/nexus3
   36c12cb044ac: Pull complete 
   8a1b09f0eced: Pull complete 
   f47ff8368d44: Pull complete 
   1f37eeb9a088: Pull complete 
   4b6419f9a540: Pull complete 
   cd8e246a9663: Pull complete 
   68721705c831: Pull complete 
   Digest: sha256:88044c8cdbbf1fea42b65b6c785bb88e4e2b2e96b3becd2bfce22f481216a951
   Status: Downloaded newer image for sonatype/nexus3:latest
   1bfde8b8401841bb82e9c00ab6e0efc90860dbbe44771e74cc13e4218d4da162
   ```

   Check the progress:

   ```console
   > docker logs -f nexus
   2023-06-21 10:27:40,499+0000 INFO  [FelixStartLevel] *SYSTEM org.sonatype.nexus.pax.logging.NexusLogActivator - start
   ...
   ```

   Get the container IP (for further reference):

   ```console
   > docker inspect --format {{.NetworkSettings.IPAddress}} nexus
   172.17.0.5
   ```

   Get the installation password:

   ```console
   > docker exec nexus cat /nexus-data/admin.password
   f76d718e-a75c-4a62-8c0a-09ca57e8a6b9
   ```

   In this case credentials will be `admin/f76d718e-a75c-4a62-8c0a-09ca57e8a6b9`.
   It is then time to complete the installation from the web ui console, by logging at:

   [http://localhost:8081](http://localhost:8081)

   And complete the installation:

   - Next
   - Chose the new password
   - Configure Anonymous Access -> Enable anonymous access
   - Finish

   Last, create a new docker repository by selecting the wheel icon and then
   `Repository` -> `Create repository` -> `docker (hosted)` with these
   specifications:

   - Name: myproject
     Select `Create an HTTP connector at specified port. Normally used if the server is behind a secure proxy.` -> 5000
     Select `Allow anonymous docker pull ( Docker Bearer Token Realm required )`

   Once `Create repository` is pressed, then the docker repo will be available at
   the 5000 port.

   Last but not least the Docker Bearer Token needs to be activated, from the
   `Security` -> `Realms` section, click on + beside the `Docker Bearer Token` 
   so that it becomes part of the `Active` group.

2. Test credentials:

   ```console
   > docker login -u admin localhost:5000
   Password: 
   WARNING! Your password will be stored unencrypted in /home/rasca/.docker/config.json.
   Configure a credential helper to remove this warning. See
   https://docs.docker.com/engine/reference/commandline/login/#credentials-store
   
   Login Succeeded
   ```

3. Move to the GitLab interface in the `CI/CD Settings` of `myproject` at:

   [http://localhost:8080/devsecops/myproject/-/settings/ci_cd](http://localhost:8080/devsecops/myproject/-/settings/ci_cd)

   Click `Expand` button of the `Variables` section and add:

   - `NEXUS_HOST`: localhost:5000
   - `NEXUS_USERNAME`: admin
   - `NEXUS_PASSWORD`: admin123

4. Add the build process to the pipeline by making the `.gitlab-ci.yml` file look
   like this:

   ```yaml
   stages:
     - build
     - sonarqube
     - publish
   
   variables:
     DOCKER_IMAGE_NAME: ncat_http_msg_port
   
   build_job:
     stage: build
     script:
       - echo "Building myproject"
       - docker build -t ${DOCKER_IMAGE_NAME} .
   
   sonarqube_job:
     stage: sonarqube
     image: sonarsource/sonar-scanner-cli:latest
     script:
       - sonar-scanner
         -Dsonar.host.url=${SONARQUBE_HOST}
         -Dsonar.login=${SONARQUBE_TOKEN}
         -Dsonar.projectKey=myproject
     only:
       - main
   
   publish_job:
     stage: publish
     script:
       - echo "Publishing image to Nexus Repository..."
       - docker login -u ${NEXUS_USERNAME} -p ${NEXUS_PASSWORD} ${NEXUS_URL}
       - docker tag ${DOCKER_IMAGE_NAME}:latest ${NEXUS_URL}/${DOCKER_IMAGE_NAME}:latest
       - docker push ${NEXUS_URL}/${DOCKER_IMAGE_NAME}:latest
     only:
       - main
   ```

   Commit and push the changes:

   ```console
   > git add .

   > git commit -m "Add container build and push"
   [main bf304ec35aa8] Add container build and push
    1 file changed, 35 insertions(+), 13 deletions(-)
    rewrite .gitlab-ci.yml (98%)

   > git push
   Enumerating objects: 5, done.
   Counting objects: 100% (5/5), done.
   Delta compression using up to 16 threads
   Compressing objects: 100% (3/3), done.
   Writing objects: 100% (3/3), 645 bytes | 645.00 KiB/s, done.
   Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
   To ssh://localhost:2222/devsecops/myproject.git
      96dcce050014..bf304ec35aa8  main -> main
   ```

   And then follow the progress from the GitLab interface.

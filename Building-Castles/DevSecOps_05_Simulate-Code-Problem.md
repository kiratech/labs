# Exercise | Block the pipeline in case of problems

1. Let's push a faulty source code to our repo:

   ```java
   package org.example;

   public class Example {
       public static void main(String[] args) {
           int x = 5;
           int y = 0;
           int result = x / y; // Division by zero error

           logger.log("Result: " + result);
       }
   }
   ```

   In this example, the code attempts to divide the variable x by y, which is
   initialized to 0. This division by zero operation will result in an exception
   at runtime, causing the program to crash or behave unexpectedly.

   SonarQube can identify this issue and raise a warning or error, indicating a
   potential bug or vulnerability in the code.

   SonarQube is designed to analyze source code for various issues such as bugs,
   code smells, security vulnerabilities, and maintainability problems.
   It applies a set of predefined rules and checks to identify potential issues
   and provide feedback to developers, enabling them to improve the quality of
   their code.

   Let's push it on the repo:

   ```
   > mkdir -p src/org/example

   > cat src/org/example/Example.java
   package org.example;

   public class Example {
       public static void main(String[] args) {
           int x = 5;
           int y = 0;
           int result = x / y; // Division by zero error

           logger.log("Result: " + result);
       }
   }

   > git add .

   > git commit -m "Simulate a faulty code"
   [main 81a9f2c6f04b] Simulate a faulty code
    1 file changed, 9 insertions(+)
    create mode 100644 src/org/example/Example.java

   > git push
   Enumerating objects: 4, done.
   Counting objects: 100% (4/4), done.
   Delta compression using up to 16 threads
   Compressing objects: 100% (3/3), done.
   Writing objects: 100% (3/3), 434 bytes | 434.00 KiB/s, done.
   Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
   To ssh://localhost:2222/devsecops/myproject.git
      b00b7e1dafee..81a9f2c6f04b  main -> main

   ```

2. Unexpectedely, the pipeline will complete with no errors. The SonarQube stage
   completes as follows:

   ```
   ...
   INFO: ------------------------------------------------------------------------
   INFO: EXECUTION SUCCESS
   INFO: ------------------------------------------------------------------------
   INFO: Total time: 5.942s
   INFO: Final Memory: 22M/114M
   INFO: ------------------------------------------------------------------------
   Job succeeded
   ```

   But by looking into the project details we will find a Failed status:

   ![DevSecOps_05_Simulate-Code-Problem_Sonarqube-Code-Failure.md](images/DevSecOps_05_Simulate-Code-Problem_Sonarqube-Code-Failure.md)

   This happens because we don't have a blocker for the pipeline.

3. It is possible to make `sonar-scanner` use the quality gate functionality,
   that will ensure that the correct result is returned from SonarQube before
   moving on.

   This can be implemented by changing the `sonarqube_job` stage, adding the
   `sonar.qualitygate.wait=true` option into the `.gitlab-ci.yml` file:

   ```yaml
   sonarqube_job:
     stage: sonarqube
     image: sonarsource/sonar-scanner-cli:latest
     script:
       - sonar-scanner
         -Dsonar.host.url=${SONARQUBE_HOST}
         -Dsonar.login=${SONARQUBE_TOKEN}
         -Dsonar.projectKey=myproject
         -Dsonar.qualitygate.wait=true
     only:
       - main
   ```

   By pushing the change:

   ```
   > git add .gitlab-ci.yml

   > git commit -m "Add quality gate"
   [main 12af23884239] Add quality gate
    1 file changed, 1 insertion(+)

   > git push
   Enumerating objects: 5, done.
   Counting objects: 100% (5/5), done.
   Delta compression using up to 16 threads
   Compressing objects: 100% (3/3), done.
   Writing objects: 100% (3/3), 329 bytes | 329.00 KiB/s, done.
   Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
   To ssh://localhost:2222/devsecops/myproject.git
      81a9f2c6f04b..12af23884239  main -> main
   ```

   A new pipeline will be started, and this should fail with a message like
   this:

   ```console
   INFO: Analysis report uploaded in 13ms
   INFO: ------------- Check Quality Gate status
   INFO: Waiting for the analysis report to be processed (max 300s)
   INFO: ------------------------------------------------------------------------
   INFO: EXECUTION FAILURE
   INFO: ------------------------------------------------------------------------
   INFO: Total time: 10.559s
   INFO: Final Memory: 21M/114M
   INFO: ------------------------------------------------------------------------
   ERROR: Error during SonarScanner execution
   ERROR: QUALITY GATE STATUS: FAILED - View details on http://172.17.0.1:9000/dashboard?id=myproject
   ERROR:
   ERROR: Re-run SonarScanner using the -X switch to enable full debug logging.
   ERROR: Job failed: exit code 1
   ```

4. To close the activity, let's fix our code, by removing the problem, the new
   code should be something like this:

   ```java
   package org.example;

   public class Example {
       public static void main(String[] args) {
           int x = 5;
           int y = 1;
           int result = x / y;

           logger.log("Result: " + result);
       }
   }
   ```

   And push it to see if the quality gate gets fixed:

   ```console
   > git add .

   > git commit -m "Fix faulty code"
   [main 146483ea9a74] Fix faulty code
    1 file changed, 2 insertions(+), 2 deletions(-)

   > git push
   Enumerating objects: 8, done.
   Counting objects: 100% (8/8), done.
   Delta compression using up to 16 threads
   Compressing objects: 100% (6/6), done.
   Writing objects: 100% (6/6), 772 bytes | 772.00 KiB/s, done.
   Total 6 (delta 2), reused 0 (delta 0), pack-reused 0
   To ssh://localhost:2222/devsecops/myproject.git
    + 12af23884239...146483ea9a74 main -> main
   ```

   The original error is not there anymore, and the pipeline should now be
   green.

5. Looking better to the analysis result, inside the `Overall code`, there's
   a `Security Hotspots` visible at:

   [http://172.17.0.1:9000/security_hotspots?id=myproject&inNewCodePeriod=false](http://172.17.0.1:9000/security_hotspots?id=myproject&inNewCodePeriod=false)

   Described as follows:

   ```console
   The busybox image runs with root as the default user. Make sure it is safe here.
   ```

   Even if this is a `MEDIUM` priority problem a solution can be applied over
   the Dockerfile, that should be modified as follows:

   ```Dockerfile
   FROM busybox

   ENV NCAT_MESSAGE "Container test"
   ENV NCAT_HEADER "HTTP/1.1 200 OK"
   ENV NCAT_PORT "8888"

   RUN addgroup -S nonroot && \
       adduser -S nonroot -G nonroot

   USER nonroot

   CMD /bin/nc -l -k -p ${NCAT_PORT} -e /bin/echo -e "${NCAT_HEADER}\n\n${NCAT_MESSAGE}"

   EXPOSE $NCAT_PORT
   ```

   And pushed:

   ```console
   > git add .

   > git commit -m "Fix Dockerfile to run as unprivileged user"
   [main fd5511ff7c60] Fix Dockerfile to run as unprivileged user
    1 file changed, 5 insertions(+), 1 deletion(-)

   > git push
   Enumerating objects: 5, done.
   Counting objects: 100% (5/5), done.
   Delta compression using up to 16 threads
   Compressing objects: 100% (3/3), done.
   Writing objects: 100% (3/3), 364 bytes | 364.00 KiB/s, done.
   Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
   To ssh://localhost:2222/devsecops/myproject.git
      146483ea9a74..fd5511ff7c60  main -> main
   ```

   The new push will produce a new analysis resulting in a full green status of
   `myproject`, visible at:

   [http://172.17.0.1:9000/dashboard?id=myproject](http://172.17.0.1:9000/dashboard?id=myproject)

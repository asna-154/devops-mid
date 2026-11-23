pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  triggers { githubPush() }

  environment {
    STUDENT_ID = 'FA23-BDS-051'
    IMAGE      = 'midterm-app'
    CONTAINER  = 'midterm-app'
  }

  stages {
    stage('Fetch latest data') {
      steps {
        checkout scm
        script { env.SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim() }
        sh 'test -f config.json && test -f dataset/train.csv && wc -l dataset/train.csv'
      }
    }
    stage('Build image and retrain') {
      steps {
        sh 'docker build --build-arg GIT_COMMIT=$SHA -t $IMAGE:latest .'
      }
    }
    stage('Test') {
      steps {
        sh 'docker run --rm $IMAGE:latest sh -c "pip install -q pytest httpx && python -m pytest -q tests"'
      }
    }
    stage('Deploy') {
      steps {
        sh '''
          docker rm -f $CONTAINER || true
          docker run -d --name $CONTAINER --restart unless-stopped -p 8000:8000 $IMAGE:latest
          for i in $(seq 1 20); do
            curl -fsS http://localhost:8000/metrics && exit 0
            sleep 2
          done
          exit 1
        '''
      }
    }
    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker tag $IMAGE:latest $DH_USER/$IMAGE:latest
            docker tag $IMAGE:latest $DH_USER/$IMAGE:$SHA
            docker push $DH_USER/$IMAGE:latest
            docker push $DH_USER/$IMAGE:$SHA
          '''
        }
      }
    }
  }

  post {
    always {
      script {
        def metrics = sh(script: 'curl -s http://localhost:8000/metrics || echo "unavailable"', returnStdout: true).trim()
        mail to: 'qasimalik@gmail.com',
             from: 'asnahammad11@gmail.com',
             subject: "[${env.STUDENT_ID}] Jenkins build #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
             body: "Student: ${env.STUDENT_ID}\nResult: ${currentBuild.currentResult}\nCommit: ${env.SHA}\nBuild: ${env.BUILD_URL}\n\nMetrics:\n${metrics}\n"
      }
    }
  }
}
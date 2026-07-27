pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build/Install') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest --collect-only -q || echo "⚠️ No tests found — pipeline validation only, add real tests before merging to main"'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t your-image-name:$BUILD_NUMBER .'
            }
        }

        stage('Push to ECR') {
    steps {
        sh '''
            aws ecr get-login-password --region us-east-1 OUR_REGION | docker login --username AWS --password-stdin 588957334147.dkr.ecr.us-east-1.amazonaws.com
            docker tag docker-jenkins-webapp:latest 588957334147.dkr.ecr.us-east-1.amazonaws.com/docker-jenkins-webapp:latest
            docker push 588957334147.dkr.ecr.us-east-1.amazonaws.com/docker-jenkins-webapp:latest
        '''
            }
        }
    }
}

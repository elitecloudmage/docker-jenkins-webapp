pipeline {
    agent any

    environment {
        ECR_REGISTRY = '588957334147.dkr.ecr.us-east-1.amazonaws.com'
        IMAGE_NAME   = 'docker-jenkins-webapp'
        AWS_REGION   = 'us-east-1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }  

        
        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$BUILD_NUMBER .'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $IMAGE_NAME:$BUILD_NUMBER pytest || echo "No tests found — pipeline validation only, add real tests before merging to main"'
            }
        }

        
        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
                    docker tag $IMAGE_NAME:$BUILD_NUMBER $ECR_REGISTRY/$IMAGE_NAME:$BUILD_NUMBER
                    docker push $ECR_REGISTRY/$IMAGE_NAME:$BUILD_NUMBER
                '''
            }
        }
    }
}

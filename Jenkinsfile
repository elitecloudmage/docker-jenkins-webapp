pipeline {
    agent any

    environment {
        ECR_REGISTRY = '588957334147.dkr.ecr.us-east-2.amazonaws.com'
        IMAGE_NAME   = '2tier-webapp-ecr'
        AWS_REGION   = 'us-east-2'
        DEPLOY_HOST  = 'ec2-user@18.225.55.198'
    }

    stages {
        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$BUILD_NUMBER .'
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $IMAGE_NAME:$BUILD_NUMBER pytest'
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

        stage('Deploy') {
            steps {
                sshagent(['ec2-ssh-key-id']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $DEPLOY_HOST "
                            cd ~/2tier-webapp && \
                            docker compose pull && \
                            docker compose up -d
                        "
                    '''
                }
            }
        }
    }
}

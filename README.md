# NLP_Text_Mining
This project was given as a part of the curriculum  of the Master 2 Statistiques
 et Informatique pour la Science des donnéEs

# Run Docker
1. install docker
2. open the terminal and enter to project directory then use this command to build image (name of image is tripadvisornlp): docker build -t tripadvisornlp .
3. run the container (name of container is nlp) by using this command: docker run -d --name nlp -p 8501:8501 tripadvisornlp
4. to open the app use this link: http://localhost:8501/

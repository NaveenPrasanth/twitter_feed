
####Build image
docker build . -t flask_image

####Run Image
docker run -d --name flask_container -p 80:80 flask_image 

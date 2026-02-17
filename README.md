# spam-ham
A FastAPI application to detect whether the entered message is spam or not. It contains the experiment notebook along with the vectorizer and model prepared during the process.

The backend in FastAPI has been containerized using **Docker** and hosted using `Elastic Container Registry` and `AWS Lambda`. The static HTML file has been hosted using `AWS Amplify`.

I've always been a little intrigued about hosting sites online. And AWS had always made me uncomfortable about how the whole thing could possibly be done. Now that I have hosted my first Machine Learning application online, it gives me an immense joy.

Here's the list of things that I learned along the way:

1. AWS has multiple services to it and there's no right and wrong way of doing things. It just depends entirely upon your preference.
1. I learned how to deploy containers and make them accessible to the frontend using ECR and AWS lambda.
1. I learned how to host static sites using AWS Amplify.
1. I learned how to build containers, push online, and learned and tackled several deployment errors like CORS.

Things I want to try in the future:
1. Add custom domains.
1. Enable Firewall protection to my application.

The link to the application can be found here: [Link](https://spamdetection.sudipshrestha.space/)

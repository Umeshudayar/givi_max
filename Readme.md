Givi – Enhanced Delivery Time Prediction System

Givi 2.0 is a delivery time prediction system that uses real addresses, road routes, and open-source mapping tools to estimate delivery time without any paid APIs. It integrates machine learning models with real-world map data to give more accurate results.

The system automatically geocodes addresses using OpenStreetMap, calculates both straight-line and real driving distances through OSRM, and predicts delivery time using LSTM and Gradient Boosting models. The frontend visualizes routes and predictions clearly on an interactive map.

Setup is simple: install dependencies, generate the enhanced dataset, start the backend using Flask, and open the frontend in a browser. The system then handles geocoding, routing, and time prediction end-to-end.

Tech stack includes Flask, TensorFlow, scikit-learn, Geopy, Leaflet.js, and OSRM. The project is completely open-source, works without Google APIs, and is suitable for testing, research, or real-world deployment.

Givi focuses on reliability, realism, and cost-free implementation — combining open data, automation, and AI to improve delivery predictions.
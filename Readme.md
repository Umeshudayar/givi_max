Givi – Enhanced Delivery Time Prediction System

Givi 2.0 is a delivery time prediction system I built to estimate delivery times based on real addresses and road routes using only open-source tools. The goal was to remove dependency on Google APIs and make it completely free, scalable, and realistic.

The system takes restaurant and delivery addresses, converts them to coordinates through OpenStreetMap (Nominatim), calculates real driving distances via OSRM, and predicts delivery time using a mix of LSTM and Gradient Boosting models. The frontend shows actual delivery routes on an interactive map.

The setup is simple: install dependencies, generate the enhanced dataset, start the Flask backend, and open the frontend in a browser. Once running, it automatically handles address geocoding, route calculation, and time prediction.

Tech Stack

Flask, TensorFlow, scikit-learn, Geopy, Leaflet.js, and OSRM.

File Structure
givi/
├── backend/
│   └── backend_api.py        # Flask backend with API endpoints
├── frontend/
│   └── index.html            # Frontend interface with map and address inputs
├── models/
│   ├── gbr_model.pkl         # Gradient Boosting model for delivery time
│   ├── lstm_model.h5         # LSTM model for sequential prediction
│   ├── scaler.pkl            # Scaler for preprocessing input data
│   ├── label_encoders.pkl    # Encoders for categorical features
│   └── feature_columns.pkl   # Saved column structure for model inputs
├── generate_enhanced_dataset.py  # Script to create dataset with addresses and routes
├── distance_calculator.py        # Handles distance computation using OSRM
├── requirements.txt              # Dependencies list
└── README.txt                    # Project documentation


Givi focuses on accuracy, simplicity, and open-source accessibility. It’s designed to give realistic predictions using real-world data while keeping the setup lightweight and transparent for developers, researchers, and startups.
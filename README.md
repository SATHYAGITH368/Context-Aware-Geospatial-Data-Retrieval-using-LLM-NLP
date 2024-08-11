# Context-Aware Geospatial Data Retrieval using LLM/NLP


The project aims to develop a context-aware Large Language Model (LLM) system capable of understanding and retrieving geospatial data based on the context provided in user queries. This system will infer implicit information and deliver relevant geospatial data, enhancing the precision and usability of geospatial data retrieval.
Solution Summary:
1. Introduces a new approach for utilizing LLMs in geospatial applications by enabling the model to retain information about spatial objects within an urban area, facilitating its ability to respond to conversational queries about these locations.
2. Straightforward yet effective framework for integrating geospatial knowledge into a pre-trained LLM, encompassing information about Points of Interest (POIs) and their locations, as well as spatial (proximity) awareness within a specific urban area.
 
  ## Detailed solution and Approach 
3. Provide simplified User Interface for GIS-domain experts to assess the output
4. Centralized Feature repository to store and manage feature data from multiple sources, ensuring consistency and reusability
5. Guardrails for our Large Language Models (LLMs) solution helps us in preventing harmful, offensive, or inappropriate content
Search capabilities offered:
1. Name Search: Name Search focus on Name (could be city, country etc name) and
locate point of interest
2. Category Search: Category Search helps in finding near by Category (could be near by hospital in a location) and locate point of interest
3. Type Search: Tell me highly rated places in input Point of interest

  ## Tools and Technology Used 
1. Adapter Style implementation to work with popular large language models (Phase-1: Integrated LLAMA 2 and OpenAI)
2. Apache Airflow for Data Integration and Transformation use case
3. Apache Feast for Feature Store Management
4. PostgreSQL – Landing or Staging location for all sourced dataset. Laster plan to leverage Text2SQL to query dataset
5. Streamlit – Interactive User Interface for this project
6. SpaCy – Named Entity recognition with SpaCy
7. Elastic Search – Used by Mordecai 3 for Geoparser and Event Geocoder


  ## How different is it from any of the other existing ideas?
1. Our solution is hybrid solution which is designed to work with open-source Llama and pay as we use model using OpenAI
2. Integrated Voice-to-text search enabling users who are not comfortable in typing
3. GeoParser capability helps in Geocoding allowing users to type point of interest (i.e. places) and system can identify the location and plot
4. Structured architecture for end-to-end data journey with proper data cataloging using Feature Store
5. GuardRail for LLM ensures reliable interaction preventing harmful and inappropriate results


## Brief solution

## STEP 1:DATA EXTRACTION
1. In this phase, we focus on sourcing public datasets for demo purposes from various websites such as Kaggle and SpaCy (All Country Geo dataset). These datasets come in different shapes and formats (e.g., JSON, CSV).
2. We use Airflow as our ETL (Extract, Transform, Load) tool to source and transform data into the desired format.
3. We have created separate pipelines, or DAGs (Directed Acyclic Graphs) in Airflow terminology, for each data source(airflowdags.py).
4. The sourced data is loaded into the landing zone, where we utilize PostgreSQL as our landing zone database.



## STEP 2:DATA LANDING ZONE
1. PostgreSQL supports PostGIS (Geographical Information Systems).
2. Our future plan is to enhance the user interface to provide an option to transform text to SQL
and execute spatial queries against PostgreSQL(india.sql).


## STEP 3:FEATURE EXTRACTION
1. After gathering data from various sources, we faced a significant challenge in managing all the collected information. To address this, we sought a platform for feature extraction and feature selection. We needed a centralized solution that would allow us to define, store, and access the features necessary for both training and serving our models.
2. Open-Source Apache Feast perfectly met our requirements. It facilitates tagging source data, defining features, ingesting them, and retrieving features on demand.
3. Essentially, Apache Feast functions as a Catalog Management System for our project.


## STEP 4:MODEL TRAINING PIPELINE
1. In our project, we aim to provide users with the option to integrate multiple large language models. We will begin with LLama 2 in the initial phase and eventually expand support to include other models.
2. The pipeline will be developed to include Feature Selection, which is the process of reducing the number of input variables when developing models. Reducing the number of input variables can decrease the computational cost of modeling and, in some cases, improve model performance.
3. The pipeline will focus on Feature Selection and the corresponding source data based on the selected features.
4. The process will involve creating text chunks and generating embeddings.
5. Embeddings will be stored in a vector database (FAISS).
6. A retrieval chain will be used for answer retrieval.
We can either use llama24.py, which runs on the CPU and has a slower response time, or llamagpu.py for faster performance. You can download the Llama2 model from this link

https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main

more references:
https://docs.llamaindex.ai/en/stable/examples/llm/llama_2_llama_cpp/






## STEP 5(a):User Interface (Usecase-1: Conversational UI)
1. A Conversational User Interface allows users to enter queries related to geospatial content. The front-end propagates these queries to a back-end service.
2. Our back-end service is built using Python Flask, which handles all requests from the user interface. This Python Flask service interacts with LLama 2 or other selected large language models.
3. Relevant information is retrieved based on the query, potentially utilizing embeddings stored in a vector database (FAISS) for efficient retrieval. Geo-coordinates are extracted from the query results, currently using regex for extraction, with plans to add custom output formatting to Guard Rail in the future.
4. The extracted coordinates are plotted on interactive maps using Folium, a Python library for creating Leaflet maps(streamlit4.py).



## STEP 5(b): User Interface (Usecase-2: Speech to Text)
1. A Conversational User Interface also allows user to record voice (context related to geospatial content).
2. The application uses a voice-to-text conversion service (Similar to Google speech-to-text) and the output text is propagated to a back-end service.
3. Our back-end service is built using Python Flask, which handles all requests from the user interface. This Python Flask service interacts with LLama 2 or other selected large language models.
4. Relevant information is retrieved based on the query, potentially utilizing embeddings stored in a vector database (FAISS) for efficient retrieval. Geo-coordinates are extracted from the query results, currently using regex for extraction, with plans to add custom output formatting to Guard Rail in the future.
5. The extracted coordinates are plotted on interactive maps using Folium, a Python library for creating Leaflet maps.(streamlit4.py)

 
##  STEP 5(c): User Interface (Usecase-3: Unstructured GeoParsing)
1. Our user interface also allows users to upload text files. Upon uploading, we extract entities such as states, countries, and cities using SpaCy Named Entity Recognition.
2. We leverage Mordecai, which performs two tasks for us: it handles Named Entity Recognition and performs searches against ElasticSearch, where all data is stored. The search utilizes the recognized entities.
3. We have pre-loaded datasets of all countries along with their coordinates into ElasticSearch. This setup can be extended by creating a separate Airflow job to load any input dataset into ElasticSearch.
4. The coordinates extracted from ElasticSearch responses are plotted on interactive maps using Folium, a Python library for creating Leaflet maps.


the steps for installation of mordecai for geoparsing is given in this link https://github.com/ahalterman/mordecai3/tree/main

## GUARDRAILS

Guardrails
1. Fast-Check and Validation: Guardrails can ensure that the information provided is accurate and reliable, reducing the chances of misinformation.
2. Consistency: Guardrails helps in maintaining consistency in responses, which is crucial for applications requiring precise information.
3. Enhanced User Trust: By ensuring safe and accurate outputs, guardrails enhance user trust in AI systems
4. Prevention of Harmful Outputs: Guardrails can prevent the generation of harmful, inappropriate, or toxic content.







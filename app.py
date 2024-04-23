from flask import Flask, request, jsonify
import weaviate
import weaviate.classes as wvc
from weaviate.classes.query import MetadataQuery

app = Flask(__name__) 

# Initialize Weaviate client
weaviate_url = "https://turtle-vinci-mtccq694.weaviate.network"
api_key = "ZElsNdQp6rOcmXzhZe7WuknuVqN6tMyKvSou"

client = weaviate.connect_to_wcs(
    cluster_url=weaviate_url,
    auth_credentials=weaviate.auth.AuthApiKey(api_key=api_key),
    headers={
        "X-HuggingFace-Api-Key": "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"  # Replace with your inference API key
    }
)


@app.route('/doodle/')
def query_handler_doodle():
    # Retrieve query parameters from the request
    query_word = request.args.get('query')
    limit = int(request.args.get('limit', 1))  # Default limit is 1 if not provided
    # Perform a text-based similarity search with the query word
    print(f"Querying Weaviate for '{query_word}' with limit {limit}")
    imageStrokeDoodle=client.collections.get("ImageStrokeDoodle")
    response=imageStrokeDoodle.query.near_text(query=query_word,limit=limit)
    # Extract relevant information from the query result
    response_data = []
    for result_object in response.objects:
        # Append the entire imageStroke array to the response
        response_data.append(result_object.properties)
    print(response_data)
    return jsonify(response_data)
    

@app.route('/doodle/add_stroke', methods=['POST'])
def add_stroke_doodle():
    # Retrieve word and stroke data from the request
    word = request.json.get('word')
    strokes = request.json.get('strokes')
    print(f"Adding stroke for '{word}'")
    imageStrokeDoodle=client.collections.get("ImageStrokeDoodle")
    response=imageStrokeDoodle.query.near_text(query=word,filters=wvc.query.Filter.by_property("nameOfImage").equal(word))
    data=response.objects
    # ----------------ADD ADDITIONAL PARAMETER ID as UIDD -------------
    
    print(data)
    if len(data) > 0:
        print("Updating existing stroke")
        # Update the existing stroke data
        existing_strokes = data[0].properties.get('strokeOfImage', [])
        existing_strokes.append(strokes)
        print(existing_strokes)
        uuid=data[0].uuid
        print(uuid)
        imageStrokeDoodle.data.update(uuid=uuid, properties={"strokeOfImage": existing_strokes})
    else:
        print("Adding new stroke")
        # Add a new stroke data
        imageStrokeDoodle=client.collections.get("ImageStrokeDoodle")
        uuid=imageStrokeDoodle.data.insert({"nameOfImage": word, "strokeOfImage": [strokes]})
    print(f"Stroke added for '{word}'")
    return jsonify({'message': 'Stroke added successfully'})

@app.route('/weaviate/')
def query_handler_weaviate():
    # Retrieve query parameters from the request
    query_word = request.args.get('query')
    limit = int(request.args.get('limit', 1))  # Default limit is 1 if not provided
    # Perform a text-based similarity search with the query word
    print(f"Querying Weaviate for '{query_word}' with limit {limit}")
    imageStroke=client.collections.get("ImageStroke")
    response=imageStroke.query.near_text(query=query_word,distance=0.7,limit=limit,return_metadata=MetadataQuery(distance=True))
    # Extract relevant information from the query result
    response_data = []
    for result_object in response.objects:
        # Append the entire imageStroke array to the response
        response_data.append(result_object.properties)
    print(response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import weaviate

app = Flask(__name__) 

# Initialize Weaviate client
weaviate_url = "https://turtle-vinci-mtccq694.weaviate.network"
api_key = "ZElsNdQp6rOcmXzhZe7WuknuVqN6tMyKvSou"

client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
    additional_headers={
        "X-HuggingFace-Api-Key": "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"  # Replace with your inference API key
    }
)


@app.route('/doodle/')
def query_handler():
    # Retrieve query parameters from the request
    query_word = request.args.get('query')
    limit = int(request.args.get('limit', 1))  # Default limit is 1 if not provided
    # Perform a text-based similarity search with the query word
    print(f"Querying Weaviate for '{query_word}' with limit {limit}")
    query_result = (
        client.query
        .get("ImageStrokeDoodle", ["nameOfImage","strokeOfImage"])
        .with_near_text({
            "concepts": [query_word],
        })
        .with_limit(limit)
        .do()
    )

    # Extract relevant information from the query result
    response_data = []
    for result_object in query_result.get('data', {}).get('Get', {}).get('ImageStrokeDoodle', []):
        # Append the entire imageStroke array to the response
        response_data.append(result_object)
    return jsonify(response_data)

@app.route('/doodle/add_stroke', methods=['POST'])
def add_stroke():
    # Retrieve word and stroke data from the request
    word = request.json.get('word')
    strokes = request.json.get('strokes')
    print(f"Adding stroke for '{word}'")
    where_filter = {
        "path": ["nameOfImage"],
        "operator": "Equal",
        "valueText": word,
    }
    query_result = (
        client.query
        .get("ImageStrokeDoodle", ["nameOfImage","strokeOfImage"])
        .with_near_text({
            "concepts": [word],
        })
        .with_where(where_filter)
        .with_additional(["id"])
        .do()
    )
    # print(query_result)
    
    # Check if there are any results
    data = query_result.get('data', {}).get('Get', {}).get('ImageStrokeDoodle', [])
    # print(len(data[0].get('strokeOfImage', [])))
    # print(data)
    if len(data) > 0:
        print("Updating existing stroke")
        # Update the existing stroke data
        existing_strokes = data[0].get('strokeOfImage', [])
        existing_strokes.append(strokes)
        uuid=data[0].get('_additional', {}).get('id', '')
        # print(uuid)
        client.data_object.update(
            class_name="ImageStrokeDoodle",
            uuid=uuid,
            data_object={"strokeOfImage": existing_strokes}
        )
    else:
        print("Adding new stroke")
        # Add a new stroke data
        client.data_object.create(class_name="ImageStrokeDoodle", data_object={"nameOfImage": word, "strokeOfImage": [strokes]})
    return jsonify({'message': 'Stroke added successfully'})

@app.route('/weaviate/')
def query_handler():
    # Retrieve query parameters from the request
    query_word = request.args.get('query')
    limit = int(request.args.get('limit', 1))  # Default limit is 1 if not provided
    # Perform a text-based similarity search with the query word
    print(f"Querying Weaviate for '{query_word}' with limit {limit}")
    query_result = (
        client.query
        .get("ImageStroke", ["nameOfImage"])
        .with_near_text({
            "concepts": [query_word],
            "distance": 0.7
        })
        .with_limit(limit)
        .do()
    )
    print(query_result)
    # Extract relevant information from the query result
    response_data = []
    for result_object in query_result.get('data', {}).get('Get', {}).get('ImageStroke', []):
        # Append the entire imageStroke array to the response
        response_data.append(result_object)
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)

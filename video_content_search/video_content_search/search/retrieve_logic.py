def search_timestamp(vector_store, query):
    results = vector_store.search_similar(query)

    if len(results) == 0:
        return {'timestamp': None,
                'query': '',
                'video_id': 'xxx',
                'message': 'No matching content is found!'}

    return {
        'timestamp': results[0][0].metadata['start_timestamp'],
        'query': 'transcript text',
        'video_id': 'xxx',
        'message': 'Successfully retrieved similar content'
    }

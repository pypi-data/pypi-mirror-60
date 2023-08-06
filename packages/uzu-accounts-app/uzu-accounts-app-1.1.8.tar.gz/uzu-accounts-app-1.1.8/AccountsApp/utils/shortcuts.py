from django.http import JsonResponse

def json_response(status, data=None, error=None):
    return JsonResponse({
        "status": status,
        "data": data,
        "error": error
    })

def dictify(query_set):
	dictionary = {}
	for k,v in query_set.items():
		dictionary[k] = v
	return dictionary

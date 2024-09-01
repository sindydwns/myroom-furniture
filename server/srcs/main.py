from myroom import encode, get_env
import json

request_query = "침대 배치해줘"
content, _ = encode(request_query, get_env())
print(content)

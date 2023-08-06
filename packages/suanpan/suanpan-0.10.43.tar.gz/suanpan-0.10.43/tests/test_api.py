from suanpan import api, g

g.apiHost = "localhost"

api.call(23576, "c684b6003a8c11eaaa9017f7aeb20672", data={"test": "data"})

import cherrypy
import cherrypy_cors
import json
import redis

# creating a redis connection
conn = redis.Redis(host='redis', port=6379, db=0)

# Updating cherrypy config to run on port 80 and 0.0.0.0
cherrypy.config.update({'server.socket_port': 80, 'server.socket_host': '0.0.0.0'})

class StockApp(object):

    # prepare response dict fetches all the records from redis hash
    def prepare_response_dict(self, results):
        response = []
        for key in results:
            response.append(conn.hgetall(key))
        return response

    # function to return 'Record Not Found' 
    def not_found(self):
        cherrypy.response.status = 404
        return json.dumps({
            'error' : 'Record not found'
        })

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        # fetch the latest date record available in redis
        latest = conn.hget('latest', 'date')
        response = []
        if latest is not None:
            # form a key of sorted set
            sorted_setkey = latest + ":sortedset"
            # find top 10 record keys using zrevrange function of redis
            top_10_results = conn.zrevrange(sorted_setkey, 0, 9)
            # call prepare_response_dict to fetch entire record from hash for top 10 keys found
            response = self.prepare_response_dict(top_10_results)
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(response)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def search(self, keyword=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if keyword is None:
            return self.not_found()
        else:
            # fetch the latest date record available in redis
            latest = conn.hget('latest', 'date')
            response = []
            if latest is not None:
                # form a key and fetch all the relevant records from redis hash
                keyword = latest + ":" + keyword.upper() + "*"
                keys = conn.keys(keyword)
                response = self.prepare_response_dict(keys)
            
            if len(response) == 0:
                return self.not_found()
            else:
                return json.dumps(response)

if __name__ == '__main__':
    # installig cherrypy cors to enable cors
    cherrypy_cors.install()
    config = {
            '/': {
                'cors.expose.on': True,
            },
    }
    # starting server
    cherrypy.quickstart(StockApp(), config=config)
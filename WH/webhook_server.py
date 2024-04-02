from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json

class WebhookServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        admission_review = json.loads(post_data.decode('utf-8'))
        print("Received admission review request:", admission_review)

        # Extract relevant information from the admission review
        request_object = admission_review['request']['object']
        namespace = request_object['metadata']['namespace']
        name = request_object['metadata']['name']

        # Perform validation
        allowed = self.validate_namespace_and_name(namespace, name)

        if not allowed:
            # If validation fails, deny the admission request
            response = self.build_admission_response(False, "Pod name does not adhere to naming convention")
        else:
            # If validation passes, allow the admission request
            response = self.build_admission_response(True, "Pod name adheres to naming convention")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def validate_namespace_and_name(self, namespace, name):
        # Validate if pod name adheres to naming convention
        if not name.startswith(namespace + "-"):
            return False
        return True

    def build_admission_response(self, allowed, message):
        return {
            "response": {
                "allowed": allowed,
                "status": {
                    "message": message
                }
            }
        }

def run(server_class=HTTPServer, handler_class=WebhookServer, port=8443):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile='server.key', certfile='server.crt', server_side=True)
    print('Starting webhook server...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()

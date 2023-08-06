import shutil, os, config, http.server, socketserver

def validate_config():
    
    passed = True

    #Make sure a user has set web
    try:
        config.web
        config.web['production']
        config.web['staging']
    except:
        passed = False
        print("**ERROR**: \nYou are missing the web dictionary from the config file.")
        print("web = dict(")
        print("   production = \"web\",")
        print("   staging = \"staging\"")
        print(")")
    
    #Make sure a user has set data
    try:
        config.data
        config.data['base']
        config.data['production']
        config.data['staging']
    except:
        passed = False
        print("**ERROR**: \nYou are missing the data dictionary from the config file.")
        print("data = dict(")
        print("   base = \"data\",")
        print("   production = \"data/data.json\",")
        print("   staging = \"data/data_staging.json\"")
        print(")")

    #Make sure a user has set non_listed_types
    try:
        config.content_path
    except:
        passed = False
        print("**ERROR**: You are missing the content_path variable from the config file")
        print("content_path = \"content\"")

    #Make sure a user has set non_listed_types
    try:
        config.non_listed_types
    except:
        passed = False
        print("**ERROR**: You are missing the non_listed_types list from the config file")
        print("non_listed_types = [\"page\", \"link\"]")
        
    if not passed:
        exit()

def preview(directory, port=8000):


    web_dir = os.path.join(os.path.dirname(__file__), "staging")

    print(web_dir)

    os.chdir(web_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print("Serving "+directory+" at http://localhost:"+ str(port))

    try: 
        httpd.serve_forever()
    except KeyboardInterrupt: 
        pass; httpd.server_close()
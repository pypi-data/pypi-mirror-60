from markdown2 import markdown
from slugify import slugify
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import os, json, readtime, shutil
import indexing, config

template_env = Environment(loader=FileSystemLoader(searchpath='./templates'))

def build_home():

    print("\n\nStarting home page build...")
    
    #Published
    with open(config.data['production'], "r") as data_file:
        render_home(data_file, 'production')

    #staging
    with open(config.data['staging'], "r") as data_file:
        render_home(data_file, 'staging')

        

def render_home(data_file, location):
    """Render the home page by passing in the contents of the 
    index file (data_file) and the location ("production" or "staging")
    """
    path = config.web[location]

    locale = location

    articles = indexing.get_articles(data_file)

    os.makedirs(os.path.dirname(path+"/index.html"), exist_ok=True)
    with open(path+"/index.html", "w") as output_file:
        template_env = Environment(loader=FileSystemLoader(searchpath='./templates'))
        template = template_env.get_template(config.home_template)
        output_file.write(
            template.render(
                title="Home page",
                articles=articles,
                meta=[],
                locale = location
            )
        )
    print("Completed "+location+" home page build")


##############

# Content

def render():
    #Render page templates
    print("\nRendering content...")
    for content_dir in Path(config.content_path).iterdir():
        content_dir = str(content_dir)
        #Ignore any hidden files/folders
        if not content_dir.startswith(config.content_path+"/."):
            if not "index.html" in content_dir:
                #Process this pice of content
                page = process_content_item(content_dir)
                if page:
                    print("Rendered: " + str(page))

def process_content_item(path):

    print("Path: "+path)

    slug = slugify(path.replace(config.content_path, ""))
    
    #Load the meta file
    with open(path+"/meta.json") as meta_file:
        meta = json.load(meta_file)

    #Render the Markdown
    try:
        with open(path+"/markdown.md") as markdown_file:
            rendered_content = markdown(markdown_file.read(),
            extras=['fenced-code-blocks', 'code-friendly'])
    except:
        print(path+"/markdown.md not found")
        
    #Published or not??
    if meta['published']:
        location = ["staging", "production"]
    else:
        location = ["staging"]

    for locale in location:
        #Move any images in to place
        images_path = path + "/images/"
        if os.path.isdir(images_path):
            images_destination = config.web[locale] + "/" + slug + "/images/"
            try:
                os.makedirs(os.path.dirname(images_destination), exist_ok=True)
                copy_files(images_path, images_destination)  
            except:
                print("Failed to copy image files for "+slug+" to "+str(locale))

        filename = config.web[locale]+"/"+slug+"/index.html"

        #Replace the meta with the meta from the index
        with open(config.data[locale], 'r') as index_file:
            all_index = json.load(index_file)
            for i, item in enumerate(all_index):
                if item['slug'] == slug:
                    meta = item
                    meta['position'] = i
        
        #Create the rendered HTML file
        create_content_html_file(filename, meta, rendered_content)
    
    return filename

def create_content_html_file(filename, meta, article):
    """Render the content for each page\n
    filename: string\n
    meta: dict\n
    article: string
    """

    template = template_env.get_template(meta['template'])
    l = str(filename.split("/")[0])
    locale = list(config.web.keys())[list(config.web.values()).index(l)]
    

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as output_file:
        output_file.write(
            template.render(
                meta=meta,
                article=article,
                locale=locale
            )
        )


##############

def copy_static_files():
    print("\nCopying static files...")

    src = "templates/static/"
    destination_production = config.web['production'] + "/static/"
    destination_staging = config.web['staging'] + "/static/"

    try:
        copy_files(src, destination_production)  
    except:
        print("Failed to copy static files to production")
    
    try:
        copy_files(src, destination_staging)  
    except:    
        print("Failed to copy static files to production")


def delete_folders():
    """Deletes the existing folders before creating a render:

    - Data folders
    - Production
    - Staging
    """

    print("\nEmptying old content...\n")

    #Delete the data files before we begin
    try:
        shutil.rmtree(config.data['base'])
    except:
        print("Data folder didn't exist")

    #Recreate blank data files
    try:
        indexing.recreate_empty_data_index()
    except:
        print("Failed to make empty data indexes")
    
    #Delete the production folder
    try:
        shutil.rmtree(config.web['production'])
    except:
        print("Production web folder didn't exist")

    #Delete the staging folder
    try:
        shutil.rmtree(config.web['staging'])
    except:
        print("Staging web folder didn't exist")

    print("\nPrevious content cleared...\n")


def collect_markdown(path):

    try:
        with open(path) as markdown_file:
            return markdown(markdown_file.read(),
            extras=['fenced-code-blocks', 'code-friendly'])
    except:
        print("\n\n*ERROR*: In '"+path+"/' markdown.md not found\n")
        exit()


def copy_files(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
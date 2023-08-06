from pathlib import Path
from slugify import slugify
from datetime import datetime
import readtime, json, os
import config, content


def recreate_empty_data_index():
    data = []
    os.makedirs(os.path.dirname(config.data['production']), exist_ok=True)
    with open(config.data['production'], 'w') as data_file:
            json.dump(data, data_file)

    os.makedirs(os.path.dirname(config.data['staging']), exist_ok=True)
    with open(config.data['staging'], 'w') as data_file:
            json.dump(data, data_file)

def build():
    for content_dir in Path("content").iterdir():
        content_item = str(content_dir)

        #Ignore any hidden files/folders
        if not content_item.startswith(config.content_path+"/."):
            print("Creating Index: " + content_item)

            #Only include items that are not in the non_listed_types array
            if include_in_list(content_item):
                print("Including " + content_item +" in the index")
                process_content_item(content_item)
            else:
                print("Excluding " + content_item +" from the index")


def process_content_item(path):

    # Read the meta information for this piece of content
    with open(path+"/meta.json") as index_file:
        meta = json.load(index_file)
    
    #Give the content a slug
    #TODO make sure the slug unique
    meta['slug'] = slugify(path.replace(config.content_path, ""))

    #Set the filename for the content to be rendered to
    # filename = config.web['production']+"/"+meta['slug']+"/index.html"
    # staging_filename = config.web['staging']+"/"+meta['slug']+"/index.html"

    article = content.collect_markdown(path+"/markdown.md")

    # Calculate the reading time
    meta['read_time'] = str(readtime.of_html(article))

    #add this content to the index
    if meta['published']:
        add_to_index(meta, "staging")
        add_to_index(meta, "production")
    else:
        add_to_index(meta, "staging")
    

def add_to_index(meta, location):

    data_file_name = config.data[location]
    
    with open(data_file_name, "r") as data_file:
        data = json.load(data_file)
    
    data.append(meta)

    with open(data_file_name, 'w') as data_file:
        json.dump(data, data_file)
        if not "draft" in data_file_name:
            print("(Production) Indexed: " + str(meta['slug']))
        else:
            print("(Staged) Indexed: " + str(meta['slug']))


def sort_articles():
    #Sort the articles by date
    with open(config.data['production'], 'r') as data_file:
        data = json.load(data_file)
        with open(config.data['production'], 'w') as data_file:
            new_datas = sorted(data, key=lambda r: datetime.strptime(r["date"], "%d/%m/%Y"), reverse=True)
            for i, new_data in enumerate(new_datas):
                new_data['position'] = i
            json.dump(new_datas, data_file)
    
    with open(config.data['staging'], 'r') as data_file:
        data = json.load(data_file)
        with open(config.data['staging'], 'w') as data_file:
            new_datas = sorted(data, key=lambda r: datetime.strptime(r["date"], "%d/%m/%Y"), reverse=True)
            for i, new_data in enumerate(new_datas):
                new_data['position'] = i
            json.dump(new_datas, data_file)


def include_in_list(path):

    #Make sure a user has set non_listed_types
    try:
        config.non_listed_types
    except:
        print("**ERROR**: You are missing the non_listed_types list from the config file")
        exit()

    # Read the meta information for this piece of content
    with open(path+"/meta.json") as meta_data:
        meta = json.load(meta_data)
        if "type" not in meta or meta['type'] not in config.non_listed_types:
            return True
        
    return False

def article_position(articles, slug):
    i = 0
    for dict in articles:
        if dict['slug'] == slug:
            return i
        i = i + 1

def get_articles(data_file):
    
    articles = json.load(data_file)
    filtered_articles = []

    for i, article in enumerate(articles):
        article['position'] = i
        filtered_articles.append(article)
    
    return filtered_articles
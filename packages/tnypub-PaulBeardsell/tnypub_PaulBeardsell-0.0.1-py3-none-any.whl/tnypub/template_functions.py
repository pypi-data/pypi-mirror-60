import json
import config, content, indexing

# ---------------- Template functions

# Previous & Next
def prevnext_article(meta, direction, locale):
        
    data_file_name = config.data[locale]
        
    with open(data_file_name, "r") as data_file:
        all_posts = json.load(data_file)
        #only include posts
        filtered_articles = []
        for i, post in enumerate(all_posts):
            if not "type" in post or post['type'] == "post":
                post['position'] = i
                filtered_articles.append(post)

    for i, article in enumerate(filtered_articles):
        if meta['slug'] == article['slug']:
            if direction == "-":
                required_position = i - 1
            else:
                required_position = i + 1
        
    if required_position >= 0 and len(filtered_articles) > required_position:
        return filtered_articles[required_position]
    else:
        return None


content.template_env.globals['prevnext_article'] = prevnext_article
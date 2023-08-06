import config, template_functions, indexing, utils, content

        
def init():

    print("\nInitialising...")

    #Make sure all the variables are set in the config
    utils.validate_config()
    
    #Delete and empty any old content
    content.delete_folders()

    #Indexing
    indexing.build()
    
    #Artciles should be shorted by date
    indexing.sort_articles()

    #Build out the home page
    content.build_home()
    
    #Render page content
    content.render()

    #Copy static directory
    content.copy_static_files()
    
    print("\nComplete.")

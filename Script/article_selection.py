def select_top_articles(ranked_specific_articles, general_articles, num_general=3):
    selected_articles = {}
    
    # Select the highest ranked article from each specific topic
    for topic, articles in ranked_specific_articles.items():
        if articles:
            selected_articles[topic] = [articles[0]]
    
    # Select top 3 general articles
    top_general = sorted(general_articles, key=lambda x: x['topic_relevance'], reverse=True)[:num_general]
    selected_articles['General'] = top_general
    
    return selected_articles

def manual_article_selection(ranked_specific_articles, general_articles):
    selected_articles = {}
    
    print("\nManual Article Selection")
    print("========================")
    
    # Select from specific topics
    for topic, articles in ranked_specific_articles.items():
        print(f"\n{topic}:")
        for i, article in enumerate(articles):
            print(f"{i+1}. {article['title']} (Relevance: {article['topic_relevance']:.2f})")
        
        selections = input(f"Enter the numbers of the articles you want to include for {topic} (comma-separated, or press Enter to skip): ")
        if selections:
            indices = [int(s.strip()) - 1 for s in selections.split(',')]
            selected_articles[topic] = [articles[i] for i in indices if i < len(articles)]
    
    # Select from general articles
    print("\nGeneral Articles:")
    for i, article in enumerate(general_articles):
        print(f"{i+1}. {article['title']} (Relevance: {article['topic_relevance']:.2f})")
    
    selections = input("Enter the numbers of the general articles you want to include (comma-separated): ")
    if selections:
        indices = [int(s.strip()) - 1 for s in selections.split(',')]
        selected_articles['General'] = [general_articles[i] for i in indices if i < len(general_articles)]
    
    return selected_articles
from tagging import aggregate_articles
from tagging import (
    preprocess_text, assign_specific_topics, rank_specific_topic_articles,
    extract_features, perform_topic_modeling, assign_topics_and_relevance,
    rank_articles_by_relevance
)
from summarizer import summarize_article, translate_content
from email_template import generate_email_content
from article_selection import select_top_articles, manual_article_selection

def main():
    print("Starting the test run...")

    # Step 1: Aggregate articles
    print("\nAggregating articles...")
    articles = aggregate_articles()
    print(f"Total articles aggregated: {len(articles)}")

    # Step 2: Preprocess and tag articles
    print("\nPreprocessing and tagging articles...")
    for article in articles:
        article['content'] = preprocess_text(f"{article['title']} {article['summary']}")
    
    articles = assign_specific_topics(articles)
    ranked_specific_articles = rank_specific_topic_articles(articles)

    # Print some stats about specific topics
    print("\nSpecific topic distribution:")
    for topic, topic_articles in ranked_specific_articles.items():
        print(f"{topic}: {len(topic_articles)} articles")

    # Step 3: Handle general articles
    general_articles = [article for article in articles if article['specific_topic'] is None]
    print(f"\nNumber of general articles: {len(general_articles)}")

    X, vectorizer = extract_features(general_articles)
    lda, topic_keywords = perform_topic_modeling(X, vectorizer, n_topics=10)
    
    general_articles = assign_topics_and_relevance(general_articles, lda, X)
    general_articles = rank_articles_by_relevance(general_articles)

    # Step 4: Article selection
    print("\nArticle selection...")
    selection_mode = input("Choose selection mode (auto/manual): ").lower()
    if selection_mode == 'manual':
        selected_articles = manual_article_selection(ranked_specific_articles, general_articles)
    else:
        selected_articles = select_top_articles(ranked_specific_articles, general_articles)

    # Print selected articles
    print("\nSelected articles:")
    for topic, articles in selected_articles.items():
        print(f"\n{topic}:")
        for article in articles:
            print(f"- {article['title']} (Relevance: {article['topic_relevance']:.2f})")

    # Step 5: Summarize selected articles
    print("\nSummarizing selected articles...")
    summarized_articles = {}
    for topic, articles in selected_articles.items():
        summarized_articles[topic] = [(article, summarize_article(article)) for article in articles]

    # Print summaries
    print("\nArticle summaries:")
    for topic, articles in summarized_articles.items():
        print(f"\n{topic}:")
        for article, summary in articles:
            print(f"- {article['title']}")
            print(f"  Summary: {summary[:100]}...")  # Print first 100 characters of summary

    # Step 6: Generate email content
    print("\nGenerating email content...")
    email_content = generate_email_content(summarized_articles)

    # Print a sample of the email content
    print("\nSample of generated email content:")
    print(email_content[:500] + "...")  # Print first 500 characters

    # Step 7: Test translation
    print("\nTesting translation...")
    languages_to_test = ['es', 'fr', 'de']  # Spanish, French, German
    for lang in languages_to_test:
        print(f"Translating to {lang}...")
        translated_content = translate_content(email_content[:1000], lang)  # Translate first 1000 characters for testing
        print(f"First 200 characters of translated content: {translated_content[:200]}")

    print("\nTest run completed!")

if __name__ == "__main__":
    main()
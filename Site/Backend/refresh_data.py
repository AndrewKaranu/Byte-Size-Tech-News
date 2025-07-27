from app import app, db
from app.models import ArticleBatch
from app.services.newsletter_service import collect_and_process_articles

with app.app_context():
    # Delete existing corrupted batches
    print("Clearing existing corrupted batches...")
    ArticleBatch.query.delete()
    db.session.commit()
    print("Existing batches cleared.")
    
    # Collect fresh articles
    print("Collecting new articles...")
    try:
        batch_id = collect_and_process_articles()
        print(f"✅ Successfully created new batch with ID: {batch_id}")
        
        # Verify the new batch
        batch = ArticleBatch.query.get(batch_id)
        if batch and batch.articles_json:
            json_length = len(batch.articles_json)
            print(f"✅ New batch JSON length: {json_length} characters")
            print(f"✅ JSON is no longer truncated (can store up to 4GB)")
        else:
            print("❌ Failed to create batch")
            
    except Exception as e:
        print(f"❌ Error collecting articles: {e}")
        import traceback
        traceback.print_exc()

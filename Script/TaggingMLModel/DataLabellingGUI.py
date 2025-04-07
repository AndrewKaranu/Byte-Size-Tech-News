import json
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import google.generativeai as genai
import os
import time
import random
import threading
from openai import OpenAI
# TODO: MARK ads for removal
# Load the API keys from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
openai_api_key = config.get('openai_api_key')
google_api_key = config.get('api_key')

# Set up OpenAI client
client = OpenAI(api_key=openai_api_key)

# Set up Google Gemini API
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-pro')

class LabelingTool:
    def __init__(self, master):
        self.master = master
        self.master.title("Article Labeling Tool")
        
        self.df = pd.read_csv('unlabeled_articles.csv')
        self.current_index = 0
        
        self.text = tk.Text(master, height=20, width=80, wrap=tk.WORD)
        self.text.pack(pady=10)
        
        self.source_label = tk.Label(master, text="")
        self.source_label.pack()
        
        self.url_label = tk.Label(master, text="", fg="blue", cursor="hand2")
        self.url_label.pack()
        self.url_label.bind("<Button-1>", self.open_url)
        
        self.view_full_button = tk.Button(master, text="View Full Article", command=self.toggle_view)
        self.view_full_button.pack(pady=5)
        
        self.ai_label_button = tk.Button(master, text="AI Label", command=self.ai_label)
        self.ai_label_button.pack(pady=5)

        self.batch_ai_label_button = tk.Button(master, text="Batch AI Label", command=self.start_batch_ai_label)
        self.batch_ai_label_button.pack(pady=5)
        
        self.topic_var = tk.StringVar()
        self.topic_dropdown = ttk.Combobox(master, textvariable=self.topic_var)
        self.topic_dropdown['values'] = ('AI', 'Web Development', 'Cybersecurity', 'Mobile Tech', 'Cloud Computing', 'Design', 'Hardware', 'Other')
        self.topic_dropdown.pack(pady=10)
        
        self.submit_button = tk.Button(master, text="Submit", command=self.submit_label)
        self.submit_button.pack(pady=10)
        
        self.progress_label = tk.Label(master, text="")
        self.progress_label.pack(pady=10)
        
        self.is_summary_view = True
        self.load_next_article()
    
    def summarize_text(self, text):
        max_retries = 3
        base_delay = 1  # Base delay in seconds
        
        for attempt in range(max_retries):
            try:
                prompt = f"Summarize the following article in 2-3 sentences:\n\n{text}"
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:  # If it's not the last attempt
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"API call failed. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    print(f"API call failed after {max_retries} attempts. Error: {str(e)}")
                    return "Unable to generate summary due to API error."
    
    def load_next_article(self):
        if self.current_index < len(self.df):
            article = self.df.iloc[self.current_index]
            self.current_article = article
            
            if 'summary' not in article or pd.isna(article['summary']):
                self.master.config(cursor="wait")
                self.master.update()
                summary = self.summarize_text(article['content'])
                self.master.config(cursor="")
                self.df.at[self.current_index, 'summary'] = summary
                self.df.to_csv('unlabeled_articles.csv', index=False)
            else:
                summary = article['summary']
            
            self.display_content(summary if self.is_summary_view else article['content'])
            self.source_label.config(text=f"Source: {article['source']}")
            self.url_label.config(text=article['url'])
            self.progress_label.config(text=f"Progress: {self.current_index + 1}/{len(self.df)}")
        else:
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, "All articles labeled!")
            self.source_label.config(text="")
            self.url_label.config(text="")
            self.progress_label.config(text="Completed!")
    
    def display_content(self, content):
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, f"Title: {self.current_article['title']}\n\n{content}")
    
    def toggle_view(self):
        self.is_summary_view = not self.is_summary_view
        content = self.current_article['summary'] if self.is_summary_view else self.current_article['content']
        self.display_content(content)
        self.view_full_button.config(text="View Full Article" if self.is_summary_view else "View Summary")
    
    def submit_label(self):
        if self.current_index < len(self.df):
            self.df.at[self.current_index, 'specific_topic'] = self.topic_var.get()
            self.current_index += 1
            self.load_next_article()
            self.df.to_csv('labeled_articles.csv', index=False)
    
    def open_url(self, event):
        import webbrowser
        webbrowser.open(self.current_article['url'])
        
    def ai_label(self):
        if self.current_index < len(self.df):
            article = self.df.iloc[self.current_index]
            label = self.get_ai_label(article['title'], article['summary'])
            self.topic_var.set(label)

    def get_ai_label(self, title, summary):
        prompt = f"Categorize the following article into one of these categories: AI, Web Development, Cybersecurity, Mobile Tech, Cloud Computing, Design, Hardware, Other. Respond with only the category name.\n\nTitle: {title}\n\nSummary: {summary}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorizes tech articles."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()

    def start_batch_ai_label(self):
        batch_size = 10  # Adjust this based on your needs
        start_index = self.current_index
        end_index = min(start_index + batch_size, len(self.df))
        
        self.progress_label.config(text="Batch labeling in progress...")
        self.batch_ai_label_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self.batch_ai_label, args=(start_index, end_index), daemon=True).start()

    def batch_ai_label(self, start_index, end_index):
        for index in range(start_index, end_index):
            article = self.df.iloc[index]
            label = self.get_ai_label(article['title'], article['summary'])
            self.df.at[index, 'specific_topic'] = label
        
        self.df.to_csv('labeled_articles.csv', index=False)
        self.master.after(0, self.batch_labeling_complete, end_index)

    def batch_labeling_complete(self, end_index):
        self.current_index = end_index
        self.load_next_article()
        self.progress_label.config(text=f"Progress: {self.current_index + 1}/{len(self.df)}")
        self.batch_ai_label_button.config(state=tk.NORMAL)
        messagebox.showinfo("Batch Labeling", "Batch labeling complete!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingTool(root)
    root.mainloop()
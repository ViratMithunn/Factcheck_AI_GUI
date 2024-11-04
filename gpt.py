from tkinter import Tk, Label, Entry, Text, Button, Scrollbar, END, messagebox
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os


load_dotenv()


model_name = "distilgpt2"  
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Function to get the transcript from YouTube
def get_transcript(url):
    try:
        video_id = url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        output = ""
        for entry in transcript:
            output += entry['text'] + "\n"
        
        transcript_text.delete("1.0", END) 
        transcript_text.insert(END, output) 
        messagebox.showinfo("Transcript", "Transcript fetched successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Could not retrieve transcript: {e}")


def check_facts():
    subtitles = transcript_text.get("1.0", END).strip()  
    if not subtitles:
        messagebox.showwarning("No Transcript", "Please fetch the transcript first.")
        return
    
    prompt = f"Analyze the following transcript from a political debate. For each statement, indicate if it is true or false. Be precise and factual.\n\n{subtitles}"
    
    
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=1000, num_return_sequences=1, temperature=0.7)
    fact_check_result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
  
    fact_check_text.delete("1.0", END)  
    fact_check_text.insert(END, fact_check_result)  
    messagebox.showinfo("Fact-Check", "Fact-checking completed.")


root = Tk()
root.title("YouTube Fact-Checker")
root.geometry("700x500")


Label(root, text="YouTube URL:").pack(pady=5)
url_entry = Entry(root, width=50)
url_entry.pack(pady=5)

fetch_button = Button(root, text="Fetch Transcript", command=lambda: get_transcript(url_entry.get()))
fetch_button.pack(pady=10)

Label(root, text="Transcript:").pack(pady=5)
transcript_text = Text(root, wrap="word", height=10, width=80)
transcript_text.pack(pady=5)


transcript_scrollbar = Scrollbar(root, command=transcript_text.yview)
transcript_scrollbar.pack(side="right", fill="y")
transcript_text.config(yscrollcommand=transcript_scrollbar.set)


check_facts_button = Button(root, text="Check Facts", command=check_facts)
check_facts_button.pack(pady=10)

Label(root, text="Fact-Checking Results:").pack(pady=5)
fact_check_text = Text(root, wrap="word", height=10, width=80)
fact_check_text.pack(pady=5)


fact_check_scrollbar = Scrollbar(root, command=fact_check_text.yview)
fact_check_scrollbar.pack(side="right", fill="y")
fact_check_text.config(yscrollcommand=fact_check_scrollbar.set)

root.mainloop()

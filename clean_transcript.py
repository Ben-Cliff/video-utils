import os
import sys
import time
import argparse
import re
import google.generativeai as genai
from dotenv import load_dotenv

def clean_transcript_with_gemini(full_transcript_text):
    """
    Cleans a long transcript using the Gemini API by processing it in chunks.

    Args:
        full_transcript_text (str): The entire sorted transcript text.

    Returns:
        str: The cleaned transcript.
    """
    print("3. Starting transcript cleanup with the Gemini API...")
    
    # Configure the Gemini API
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        sys.exit(1)
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')

    # Process the transcript in chunks to avoid API limits
    lines = full_transcript_text.split('\n')
    chunk_size = 250  # Number of lines per chunk
    cleaned_chunks = []
    
    prompt_template = """
    The following is a raw, unordered, and fragmented transcript extracted from a video using OCR. 
    It contains many errors, repetitions, and short, disconnected phrases. 
    Your task is to process this chunk of text and clean it up into a coherent, readable paragraph.

    Instructions:
    1.  Combine related fragments into complete sentences.
    2.  Correct obvious OCR errors (e.g., "hell0" should be "hello").
    3.  Remove any timestamps or metadata-like text (e.g., "57:45").
    4.  Produce a single, well-formatted block of text. Do not add any commentary.

    Raw Transcript Chunk:
    ---
    {chunk_text}
    ---

    Cleaned Text:
    """

    num_chunks = (len(lines) + chunk_size - 1) // chunk_size
    print(f"   Processing {len(lines)} lines in {num_chunks} chunks.")
    
    for i in range(0, len(lines), chunk_size):
        chunk_number = (i // chunk_size) + 1
        print(f"   - Processing chunk {chunk_number} of {num_chunks}...")
        chunk_lines = lines[i:i+chunk_size]
        chunk_text = '\n'.join(chunk_lines)
        
        prompt = prompt_template.format(chunk_text=chunk_text)
        
        try:
            response = model.generate_content(prompt)
            cleaned_chunks.append(response.text)
            # Simple rate limiting to avoid overwhelming the API
            time.sleep(1)
        except Exception as e:
            print(f"   An error occurred while processing chunk {chunk_number}: {e}")
            cleaned_chunks.append(f"[-- ERROR PROCESSING CHUNK --]\n{chunk_text}")

    print("4. Gemini processing finished.")
    return "\n\n".join(cleaned_chunks)


def main(input_filepath):
    """
    Main function to parse, sort, and clean a raw transcript file.
    """
    print(f"1. Reading raw transcript from: {input_filepath}")
    try:
        with open(input_filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {input_filepath}")
        sys.exit(1)

    # Regex to find all text and time entries
    pattern = re.compile(r"Text: (.*?)\n  Time: ([\d.]+)s to ([\d.]+)s", re.DOTALL)
    matches = pattern.findall(content)

    if not matches:
        print("Error: No text entries found in the expected format.")
        sys.exit(1)

    print(f"2. Found and parsed {len(matches)} text segments. Sorting chronologically.")
    
    # Convert matches to a list of dictionaries and sort by start time
    annotations = []
    for text, start_time, end_time in matches:
        annotations.append({
            "text": text.strip(),
            "start_time": float(start_time)
        })
    
    annotations.sort(key=lambda x: x['start_time'])

    # Combine the sorted text into a single block
    full_sorted_text = '\n'.join([ann['text'] for ann in annotations])

    # Clean the transcript with Gemini
    cleaned_transcript = clean_transcript_with_gemini(full_sorted_text)
    
    # Save the cleaned transcript
    base, ext = os.path.splitext(input_filepath)
    cleaned_output_filename = f"{base}.cleaned{ext}"
    
    print(f"5. Saving cleaned transcript to: {cleaned_output_filename}")
    with open(cleaned_output_filename, "w") as f:
        f.write(cleaned_transcript)

    print("✅ Transcript cleaning complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cleans a raw OCR transcript file using the Gemini API."
    )
    parser.add_argument(
        "input_filepath",
        help="The path to the raw transcript file (e.g., 'output/transcript.txt').",
    )
    args = parser.parse_args()
    main(args.input_filepath)

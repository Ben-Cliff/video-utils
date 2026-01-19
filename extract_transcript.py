import os
import sys
import time
import argparse
from google.cloud import videointelligence

def analyze_video_transcript(gcs_uri):
    """
    Analyzes a video file for text transcription and returns the transcript.

    Args:
        gcs_uri (str): The GCS URI of the video file to analyze.
            (e.g., "gs://your-bucket-name/your-video.mp4")
    """
    if not gcs_uri.startswith("gs://"):
        print("Error: Video file must be a GCS URI (e.g., gs://your-bucket/your-file.mp4)")
        sys.exit(1)

    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.Feature.TEXT_DETECTION]

    print(f"1. Starting video processing for: {gcs_uri}")

    operation = video_client.annotate_video(
        request={
            "features": features,
            "input_uri": gcs_uri,
        }
    )

    print(f"2. Operation '{operation.operation.name}' started. Waiting for completion...")

    last_check = time.time()
    while not operation.done():
        if time.time() - last_check > 15:
            print(f"   [{time.strftime('%H:%M:%S')}] Still processing...")
            last_check = time.time()
        time.sleep(5)

    result = operation.result()
    print("3. Processing finished.")

    # Get the first result because we only process one video.
    annotation_result = result.annotation_results[0]

    if not annotation_result.text_annotations:
        print("No text found in the video.")
        return

    print(f"4. Found {len(annotation_result.text_annotations)} text segments.")

    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = os.path.join(output_dir, os.path.basename(gcs_uri) + ".txt")

    print(f"5. Saving transcript to: {output_filename}")

    with open(output_filename, "w") as f:
        for text_annotation in annotation_result.text_annotations:
            f.write(f"Text: {text_annotation.text}\n")

            # Get the first segment of the text annotation
            segment = text_annotation.segments[0]
            start_time = segment.segment.start_time_offset
            end_time = segment.segment.end_time_offset
            f.write(f"  Time: {start_time.seconds + start_time.microseconds / 1e6}s to {end_time.seconds + end_time.microseconds / 1e6}s\n\n")

    print("✅ Transcript saved successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extracts on-screen text from a video file using the Google Cloud Video Intelligence API."
    )
    parser.add_argument(
        "gcs_uri",
        help="The GCS URI of the video file to analyze (e.g., gs://your-bucket/your-file.mp4)",
    )
    args = parser.parse_args()

    analyze_video_transcript(args.gcs_uri)
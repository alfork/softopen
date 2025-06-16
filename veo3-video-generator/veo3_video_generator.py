#!/usr/bin/env python3
"""
Veo 3 Video Generation Script

This script generates videos using Google's Veo 3 model with your own images or clips.
Images and videos must be stored on Google Cloud Storage (GCS) for direct integration.

Prerequisites:
- Google Cloud account with Vertex AI API enabled
- Python environment with google-genai installed
- Images or video clips uploaded to a GCS bucket
- Proper authentication configured (GOOGLE_APPLICATION_CREDENTIALS)

Usage:
    python veo3_video_generator.py --prompt "Your video prompt" --image-uri "gs://bucket/image.png" --output-uri "gs://bucket/output/"
"""

import time
import argparse
import sys
from pathlib import Path
from google import genai
from google.genai.types import GenerateVideosConfig, Image


class Veo3VideoGenerator:
    """Main class for generating videos with Veo 3"""
    
    def __init__(self):
        """Initialize the Veo 3 client"""
        try:
            self.client = genai.Client()
            print("✅ Successfully initialized Veo 3 client")
        except Exception as e:
            print(f"❌ Failed to initialize Veo 3 client: {e}")
            print("Make sure GOOGLE_APPLICATION_CREDENTIALS is set and valid")
            sys.exit(1)
    
    def generate_video(self, prompt, image_uri, image_mime_type, output_gcs_uri, aspect_ratio="16:9", duration=None, seed=None):
        """
        Generate a video using Veo 3
        
        Args:
            prompt (str): Text description for the video generation
            image_uri (str): GCS URI of the input image (e.g., gs://bucket/image.png)
            image_mime_type (str): MIME type of the image (image/png or image/jpeg)
            output_gcs_uri (str): GCS URI where the generated video will be saved
            aspect_ratio (str): Video aspect ratio ("16:9" or "9:16")
            duration (int, optional): Video duration in seconds
            seed (int, optional): Random seed for reproducible results
        
        Returns:
            str: GCS URI of the generated video if successful, None otherwise
        """
        print(f"🎬 Starting video generation...")
        print(f"   Prompt: {prompt}")
        print(f"   Input image: {image_uri}")
        print(f"   Output location: {output_gcs_uri}")
        print(f"   Aspect ratio: {aspect_ratio}")
        
        try:
            config_params = {
                "aspect_ratio": aspect_ratio,
                "output_gcs_uri": output_gcs_uri,
            }
            
            if duration:
                config_params["duration"] = duration
            if seed:
                config_params["seed"] = seed
            
            operation = self.client.models.generate_videos(
                model="veo-3.0-generate-preview",
                prompt=prompt,
                image=Image(
                    gcs_uri=image_uri,
                    mime_type=image_mime_type,
                ),
                config=GenerateVideosConfig(**config_params),
            )
            
            print("⏳ Video generation started. Waiting for completion...")
            
            while not operation.done:
                print("   Still processing... (checking again in 15 seconds)")
                time.sleep(15)
                operation = self.client.operations.get(operation)
            
            if operation.response:
                video_uri = operation.result.generated_videos[0].video.uri
                print(f"✅ Video generation completed successfully!")
                print(f"📹 Generated video GCS URI: {video_uri}")
                return video_uri
            else:
                print("❌ Video generation failed or is still in progress")
                if hasattr(operation, 'error') and operation.error:
                    print(f"Error details: {operation.error}")
                return None
                
        except Exception as e:
            print(f"❌ Error during video generation: {e}")
            return None
    
    def validate_gcs_uri(self, uri):
        """Validate that a URI is a proper GCS URI"""
        if not uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {uri}. Must start with 'gs://'")
        return True
    
    def detect_mime_type(self, image_uri):
        """Detect MIME type from image URI extension"""
        uri_lower = image_uri.lower()
        if uri_lower.endswith('.png'):
            return 'image/png'
        elif uri_lower.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        else:
            raise ValueError(f"Unsupported image format. Use PNG or JPEG. Got: {image_uri}")


def main():
    """Main function to handle command line arguments and run video generation"""
    parser = argparse.ArgumentParser(
        description="Generate videos using Veo 3 with your own images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python veo3_video_generator.py --prompt "A sunrise over mountains" --image-uri "gs://my-bucket/sunrise.png" --output-uri "gs://my-bucket/videos/"
  
  python veo3_video_generator.py --prompt "Ocean waves crashing" --image-uri "gs://my-bucket/ocean.jpg" --output-uri "gs://my-bucket/videos/" --aspect-ratio "9:16"
        """
    )
    
    parser.add_argument(
        "--prompt", 
        required=True,
        help="Text description for video generation (e.g., 'A sunrise over a mountain range')"
    )
    
    parser.add_argument(
        "--image-uri",
        required=True,
        help="GCS URI of input image (e.g., 'gs://your-bucket/your-image.png')"
    )
    
    parser.add_argument(
        "--output-uri",
        required=True,
        help="GCS URI where generated video will be saved (e.g., 'gs://your-bucket/output-folder/')"
    )
    
    parser.add_argument(
        "--aspect-ratio",
        choices=["16:9", "9:16"],
        default="16:9",
        help="Video aspect ratio (default: 16:9)"
    )
    
    parser.add_argument(
        "--mime-type",
        choices=["image/png", "image/jpeg"],
        help="MIME type of input image (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        help="Video duration in seconds (optional)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible results (optional)"
    )
    
    args = parser.parse_args()
    
    generator = Veo3VideoGenerator()
    
    try:
        generator.validate_gcs_uri(args.image_uri)
        generator.validate_gcs_uri(args.output_uri)
        
        mime_type = args.mime_type
        if not mime_type:
            mime_type = generator.detect_mime_type(args.image_uri)
            print(f"🔍 Auto-detected MIME type: {mime_type}")
        
        result_uri = generator.generate_video(
            prompt=args.prompt,
            image_uri=args.image_uri,
            image_mime_type=mime_type,
            output_gcs_uri=args.output_uri,
            aspect_ratio=args.aspect_ratio,
            duration=args.duration,
            seed=args.seed
        )
        
        if result_uri:
            print(f"\n🎉 Success! Your video is ready at: {result_uri}")
            sys.exit(0)
        else:
            print(f"\n💥 Video generation failed. Check the error messages above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

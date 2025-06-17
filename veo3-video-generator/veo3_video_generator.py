#!/usr/bin/env python3
"""
Veo 3 Video Generation Script

This script generates videos using Google's Veo 3 model with your own images or clips.
Uses the official Vertex AI REST API for direct integration.

Prerequisites:
- Google Cloud account with Vertex AI API enabled
- Python environment with requests library
- Images or video clips accessible (local files or GCS)
- Proper authentication configured (GOOGLE_APPLICATION_CREDENTIALS)

Usage:
    python veo3_video_generator.py --prompt "Your video prompt" \\
        --image-uri "gs://bucket/image.png" --output-uri "gs://bucket/output/"
"""

import time
import argparse
import sys
import requests
import json
import base64
import os
from pathlib import Path
import subprocess


class Veo3VideoGenerator:
    """Main class for generating videos with Veo 3"""

    def __init__(self, project_id=None):
        """Initialize the Veo 3 client"""
        self.project_id = project_id or self._get_project_id()
        self.base_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models"
        self.access_token = None
        
        try:
            self.access_token = self._get_access_token()
            print("✅ Successfully initialized Veo 3 client with Vertex AI REST API")
        except Exception as e:
            print(f"❌ Failed to initialize Veo 3 client: {e}")
            print("Make sure GOOGLE_APPLICATION_CREDENTIALS is set and valid")
            sys.exit(1)

    def _get_project_id(self):
        """Get Google Cloud project ID from environment or gcloud config"""
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if project_id:
            return project_id
        
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ Could not determine project ID: {e}")
            print("Set GOOGLE_CLOUD_PROJECT environment variable or run 'gcloud config set project PROJECT_ID'")
            sys.exit(1)

    def _get_access_token(self):
        """Get access token for Google Cloud authentication"""
        try:
            result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ Could not get access token: {e}")
            print("Run 'gcloud auth login' to authenticate")
            sys.exit(1)

    def generate_video(
        self,
        prompt,
        image_uri=None,
        image_mime_type=None,
        output_gcs_uri=None,
        aspect_ratio="16:9",
        duration=5,
        seed=None,
        model_id="veo-3.0-generate-preview"
    ):
        """
        Generate a video using Veo 3

        Args:
            prompt (str): Text description for the video generation
            image_uri (str, optional): Path to local image file or GCS URI
            image_mime_type (str, optional): MIME type of the image (image/png or image/jpeg)
            output_gcs_uri (str, optional): GCS URI where the generated video will be saved
            aspect_ratio (str): Video aspect ratio ("16:9" or "9:16")
            duration (int): Video duration in seconds (5-8)
            seed (int, optional): Random seed for reproducible results
            model_id (str): Model ID to use

        Returns:
            str: GCS URI of the generated video if successful, None otherwise
        """
        print("🎬 Starting video generation...")
        print(f"   Prompt: {prompt}")
        if image_uri:
            print(f"   Input image: {image_uri}")
        if output_gcs_uri:
            print(f"   Output location: {output_gcs_uri}")
        print(f"   Duration: {duration} seconds")

        try:
            instances = []
            instance = {"prompt": prompt}
            
            if image_uri:
                if image_uri.startswith('gs://'):
                    print("❌ GCS URI image input not yet supported in this implementation")
                    print("Please provide a local image file path")
                    return None
                else:
                    image_data = self._encode_image_to_base64(image_uri)
                    if not image_mime_type:
                        image_mime_type = self.detect_mime_type(image_uri)
                    
                    instance["image"] = {
                        "bytesBase64Encoded": image_data,
                        "mimeType": image_mime_type
                    }
            
            instances.append(instance)
            
            parameters = {
                "sampleCount": 1,
                "durationSeconds": duration
            }
            
            if output_gcs_uri:
                parameters["storageUri"] = output_gcs_uri
            
            if seed:
                parameters["seed"] = seed

            request_data = {
                "instances": instances,
                "parameters": parameters
            }

            url = f"{self.base_url}/{model_id}:predictLongRunning"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            print("⏳ Sending video generation request...")
            response = requests.post(url, headers=headers, json=request_data)
            
            if response.status_code != 200:
                print(f"❌ API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None

            operation_data = response.json()
            operation_name = operation_data.get("name")
            
            if not operation_name:
                print("❌ No operation name returned from API")
                return None

            print(f"✅ Video generation started. Operation: {operation_name}")
            
            return self._poll_operation(operation_name, model_id)

        except Exception as e:
            print(f"❌ Error during video generation: {e}")
            return None

    def _encode_image_to_base64(self, image_path):
        """Encode local image file to base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error encoding image: {e}")
            raise

    def _poll_operation(self, operation_name, model_id):
        """Poll the long-running operation for completion"""
        print("⏳ Polling for video generation completion...")
        
        url = f"{self.base_url}/{model_id}:fetchPredictOperation"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "operationName": operation_name
        }
        
        max_attempts = 60  # 15 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.post(url, headers=headers, json=request_data)
                
                if response.status_code != 200:
                    print(f"❌ Polling failed with status {response.status_code}")
                    return None
                
                result = response.json()
                
                if result.get("done"):
                    if "response" in result:
                        predictions = result["response"].get("predictions", [])
                        if predictions and len(predictions) > 0:
                            video_uri = predictions[0].get("videoUri")
                            if video_uri:
                                print("✅ Video generation completed successfully!")
                                print(f"📹 Generated video URI: {video_uri}")
                                return video_uri
                        
                        print("❌ No video URI found in response")
                        return None
                    elif "error" in result:
                        print(f"❌ Video generation failed: {result['error']}")
                        return None
                else:
                    print(f"   Still processing... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(15)
                    attempt += 1
                    
            except Exception as e:
                print(f"❌ Error polling operation: {e}")
                return None
        
        print("❌ Video generation timed out")
        return None

    def validate_gcs_uri(self, uri):
        """Validate that a URI is a proper GCS URI"""
        if not uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {uri}. Must start with 'gs://'")
        return True

    def detect_mime_type(self, image_uri):
        """Detect MIME type from image URI extension"""
        uri_lower = image_uri.lower()
        if uri_lower.endswith(".png"):
            return "image/png"
        elif uri_lower.endswith((".jpg", ".jpeg")):
            return "image/jpeg"
        else:
            raise ValueError(
                f"Unsupported image format. Use PNG or JPEG. Got: {image_uri}"
            )


def main():
    """Main function to handle command line arguments and run video generation"""
    parser = argparse.ArgumentParser(
        description="Generate videos using Veo 3 with your own images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python veo3_video_generator.py --prompt "A sunrise over mountains" \\
    --image-uri "gs://my-bucket/sunrise.png" --output-uri "gs://my-bucket/videos/"


  python veo3_video_generator.py --prompt "Ocean waves crashing" \\
    --image-uri "gs://my-bucket/ocean.jpg" --output-uri "gs://my-bucket/videos/" \\
    --aspect-ratio "9:16"
        """,
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="Text description for video generation "
        "(e.g., 'A sunrise over a mountain range')",
    )

    parser.add_argument(
        "--image-uri",
        required=True,
        help="GCS URI of input image "
        "(e.g., 'gs://your-bucket/your-image.png')",
    )

    parser.add_argument(
        "--output-uri",
        required=True,
        help="GCS URI where generated video will be saved "
        "(e.g., 'gs://your-bucket/output-folder/')",
    )

    parser.add_argument(
        "--aspect-ratio",
        choices=["16:9", "9:16"],
        default="16:9",
        help="Video aspect ratio (default: 16:9)",
    )

    parser.add_argument(
        "--mime-type",
        choices=["image/png", "image/jpeg"],
        help="MIME type of input image (auto-detected if not specified)",
    )

    parser.add_argument(
        "--duration", type=int, help="Video duration in seconds (optional)"
    )

    parser.add_argument(
        "--seed", type=int, help="Random seed for reproducible results (optional)"
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
            seed=args.seed,
        )

        if result_uri:
            print(f"\n🎉 Success! Your video is ready at: {result_uri}")
            sys.exit(0)
        else:
            print("\n💥 Video generation failed. Check the error messages above.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

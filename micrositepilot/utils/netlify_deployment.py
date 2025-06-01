import os
import uuid
import requests
import hashlib


def deploy_html_file_with_digest(title, html_file_path, access_token=None):
    """
    Deploy a single HTML file to Netlify using the file digest method.

    Args:
        title (str): The title/name for the site
        html_file_path (str): Path to the HTML file to deploy
        access_token (str): Netlify personal access token (optional, will use env var if not provided)

    Returns:
        dict: Response containing site information and deploy details
    """
    # Use provided token or get from environment
    token = access_token or os.getenv("NETLIFY_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError("No Netlify access token provided")

    # Generate a random site name
    site_name = f"{title.lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"

    # Netlify API base URL
    api_base = "https://api.netlify.com/api/v1"

    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "MicrositePilot-Deployer",
        "Content-Type": "application/json",
    }

    try:
        # Step 1: Create a new site
        site_data = {
            "name": site_name,
            "processing_settings": {"html": {"pretty_urls": True}},
        }

        site_response = requests.post(
            f"{api_base}/sites", headers=headers, json=site_data
        )
        site_response.raise_for_status()
        site_info = site_response.json()

        site_id = site_info["id"]
        site_url = site_info["url"]
        admin_url = site_info["admin_url"]

        # Step 2: Read the HTML file and calculate SHA1
        with open(html_file_path, "rb") as f:
            html_content = f.read()

        # Calculate SHA1 hash
        sha1_hash = hashlib.sha1(html_content).hexdigest()

        # Step 3: Create deployment with file digest

        deploy_data = {"files": {"/index.html": sha1_hash}}

        deploy_response = requests.post(
            f"{api_base}/sites/{site_id}/deploys",
            headers=headers,
            json=deploy_data,
        )
        deploy_response.raise_for_status()
        deploy_info = deploy_response.json()

        deploy_id = deploy_info["id"]
        required_files = deploy_info.get("required", [])
        deploy_url = deploy_info.get("deploy_url", "")
        deploy_state = deploy_info.get("state", "unknown")

        # Step 4: Upload required files
        if sha1_hash in required_files:
            file_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "text/html",
                "User-Agent": "MicrositePilot-Deployer",
            }

            upload_response = requests.put(
                f"{api_base}/deploys/{deploy_id}/files/index.html",
                headers=file_headers,
                data=html_content,
            )
            upload_response.raise_for_status()
            print(f"✅ File uploaded successfully!")
        else:
            print(f"ℹ️  File already exists on Netlify, no upload needed")

        # Step 5: Check final deployment status
        status_response = requests.get(
            f"{api_base}/deploys/{deploy_id}", headers=headers
        )
        status_response.raise_for_status()
        status_info = status_response.json()

        final_state = status_info.get("state", "unknown")
        final_url = status_info.get("deploy_url", deploy_url)

        # Return comprehensive information
        return {
            "success": True,
            "site": {
                "id": site_id,
                "name": site_name,
                "url": site_url,
                "admin_url": admin_url,
            },
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to deploy {title}",
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "File not found",
            "message": f"HTML file {html_file_path} not found",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Unexpected error during deployment of {title}",
        }

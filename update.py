import subprocess
import os
import time
import json

# Configuration
current_directory = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_directory, "lobe.env")  # Ensure env file path is correct
container_name = "lobe-chat"
image_name = "lobehub/lobe-chat"
port_mapping = "3210:3210"


def run_command(command):
    """Run a system command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
    return result.stdout.strip()


def container_exists(container_name):
    """Check if the Docker container exists."""
    result = run_command(f"docker ps -a -q -f name={container_name}")
    return bool(result)


def build_local_image():
    """Build a Docker image from a local Dockerfile."""
    print("Building Docker image from local Dockerfile...")
    build_command = f"docker build -t {image_name} ."
    build_output = run_command(build_command)
    if "Successfully built" in build_output:
        print("Docker image built successfully.")
    else:
        print("Failed to build Docker image.")
        print(build_output)


def stop_and_remove_container(container_name):
    """Stop and remove the existing Docker container if it is running."""
    print(f"Stopping and removing the container: {container_name}...")
    if container_exists(container_name):
        run_command(f"docker stop {container_name}")
        run_command(f"docker rm {container_name}")
        print(f"Container {container_name} stopped and removed.")
    else:
        print(f"Container {container_name} does not exist. Skipping removal.")


def pull_latest_image():
    """Pull the latest Docker image for LobeChat."""
    print("Pulling the latest Docker image for LobeChat...")
    output = run_command(f"docker pull {image_name}:latest")
    print(output)
    return output


def is_image_up_to_date(output):
    """Check if the Docker image is already up to date."""
    return "Image is up to date" in output


def run_new_container():
    """Run a new Docker container with the updated image."""
    print("Starting a new Docker container with the latest image...")

    # Create a custom resolv.conf file for the container to avoid the issue
    custom_resolv_path = os.path.join(current_directory, "custom_resolv.conf")
    with open(custom_resolv_path, "w") as resolv_file:
        resolv_file.write("nameserver 8.8.8.8\n")
        resolv_file.write("nameserver 8.8.4.4\n")

    # Run the container with a custom resolv.conf file mounted
    command = (
        f"docker run -d -p {port_mapping} --env-file \"{env_file_path}\" --name {container_name} "
        f"--restart always --dns 8.8.8.8 --dns 8.8.4.4 "
        f"-v {custom_resolv_path}:/etc/resolv.conf {image_name}"
    )

    output = run_command(command)
    if "Error" not in output:
        print("New container started.")
    else:
        print("Error starting new container.")
        print(output)




def clean_up_unused_images():
    """Clean up unused Docker images."""
    print("Cleaning up unused Docker images...")
    run_command("docker image prune -f")
    print("Unused Docker images cleaned up.")


def get_image_version():
    """Get the version of the latest Docker image."""
    print("Retrieving LobeChat image version...")
    result = run_command(f"docker inspect {image_name}:latest")
    if result:
        try:
            # Load the output as JSON and extract the version information
            image_info = json.loads(result)
            version_info = image_info[0]['Config']['Labels'].get('org.opencontainers.image.version', 'Unknown version')
            print(f"Version: {version_info}")
        except (IndexError, KeyError, json.JSONDecodeError) as e:
            print(f"Error extracting version: {e}")
    else:
        print("Error retrieving image information.")


# ####### PULLING LATEST IMAGE  ########
# def main():
#     # Stop and remove the old container
#     stop_and_remove_container(container_name)

#     # Pull the latest image
#     output = pull_latest_image()

#     # Check if the image is already up to date
#     if is_image_up_to_date(output):
#         print("Lobe-Chat is already up to date. No further actions required.")
#         # Check if the container needs to be started
#         if not container_exists(container_name):
#             print("Container does not exist. Starting a new container...")
#             run_new_container()
#     else:
#         print("Detected Lobe-Chat update.")

#         # Run a new container with the updated image
#         run_new_container()

#         # Print update time and version
#         print(f"Update time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
#         get_image_version()

#     # Clean up unused images
#     clean_up_unused_images()

# #######  BUILDING IMAGE FROM DOCKERFILE  ########


def main():
    # Stop and remove the old container
    stop_and_remove_container(container_name)

    # Build the local Docker image
    build_local_image()

    # Run a new container with the updated image
    run_new_container()

    # Print update time and version
    print(f"Update time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    get_image_version()

    # Clean up unused images
    clean_up_unused_images()


if __name__ == "__main__":
    main()

import os


def traverse_folder(folder_path, ignore_folders):
    file_dict = {}

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in ignore_folders]

        file_dict[root] = files

    return file_dict


if __name__ == "__main__":
    folder_path = "/Users/simon.stipcich/code/repo/langchain-lab/"
    ignore_folders = ["__pycache__", ".git", "venv"]
    files = traverse_folder(folder_path, ignore_folders)
    print(files)

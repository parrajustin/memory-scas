
from os import remove, listdir

if __name__ == '__main__':
    # Specify the directory path (use "." for the current directory)
    directory_path = "./scan1_crop"

    # Get a list of all files and directories in the specified directory
    filenames = listdir(directory_path)

    # Print each filename
    # endFileNames = []
    for filename in filenames:
        if not filename.endswith("_back.png"):
            continue
        print(f"Removing file {filename}")
        try:
            remove(f"{directory_path}/{filename}")
            print(f"File '{filename}' deleted successfully.")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except PermissionError:
            print(f"You don't have permission to delete '{filename}'.")
        # endFileNames.append(f"./scan2_crop/{filename}")
    # print(endFileNames)


from os import remove, listdir, makedirs
import subprocess

if __name__ == '__main__':
    # Specify the directory path (use "." for the current directory)
    directory_path = "./scan2_crop"
    results_dir = f"{directory_path}_jpg"
    makedirs(results_dir, exist_ok=True)

    # Get a list of all files and directories in the specified directory
    filenames = listdir(directory_path)

    # Print each filename
    # endFileNames = []
    for filename in filenames:
        fileNameWithoutExt = filename.split(".")[0]

        print(fileNameWithoutExt)
        subprocess.run(["/home/jrparra/ffmpeg/ffmpeg", "-i", f"{directory_path}/{fileNameWithoutExt}.png", "-q:v", "2", f"{results_dir}/{fileNameWithoutExt}.jpg"], capture_output=True, text=True)
        subprocess.run(["exiftool", "-TagsFromFile", f"{directory_path}/{fileNameWithoutExt}.png", "\"-all:all>all:all\"", "-overwrite_original", f"{results_dir}/{fileNameWithoutExt}.jpg"], capture_output=True, text=True)
        # ~/ffmpeg/ffmpeg -i scan_0.png -q:v 2 output.jpg
        # exiftool -TagsFromFile scan_0.png "-all:all>all:all" output.jpg
        # endFileNames.append(f"./scan2_crop/{filename}")
    # print(endFileNames)

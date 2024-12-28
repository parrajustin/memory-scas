import easyocr
import pytesseract

if __name__ == "__main__":
    
    reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory
    result = reader.readtext('../text.png')
    # Print the extracted text
    for detection in result:
        print(detection[1])
    print("====")
    print(result)
    print("====")

    text = pytesseract.image_to_string('../text.png')
    print(text)

    print("Hello, world!")
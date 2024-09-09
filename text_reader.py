def read_chapter(chapter_no=1):
    file_path = f"chapter-{chapter_no}.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error extracting text from file: {e}")
    return ""

if __name__ == '__main__': #test code
    
    for i in range(0,6):
        print(read_chapter(i+1))
